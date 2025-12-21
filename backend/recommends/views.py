from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from movies.models import Movie, Genre, Person
from movies.serializers import MovieListSerializer, PersonSerializer

from reviews.models import Review
try:
    from reviews.models import ReviewLike
except Exception:
    ReviewLike = None

try:
    from accounts.models import Follow
except Exception:
    Follow = None

from .services.ai import run_taste_ai
from .models import TastePromptLog


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_taste(request):
    """
    POST /api/recommends/ai/
    body: { "message": "...", "history": [...] }
    return: { "answer": "...", "movies": [...], "filters": {...} }
    """
    message = (request.data.get("message") or "").strip()
    history = request.data.get("history") or []

    if not message:
        return Response({"detail": "message가 비었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    data, raw = run_taste_ai(message, history=history)

    # 로그 저장(원치 않으면 이 블록 통째로 지워도 됨)
    try:
        TastePromptLog.objects.create(
            user=request.user,
            prompt=message,
            response_raw=raw,
            response_json=data if isinstance(data, dict) else None,
        )
    except Exception:
        pass

    filters = (data.get("filters") or {}) if isinstance(data, dict) else {}
    genre_names = filters.get("genre_names") or []
    keywords = filters.get("keywords") or []
    min_vote = float(filters.get("min_vote") or 0)

    qs = Movie.objects.all().prefetch_related("genres")

    # 장르 이름 -> Genre 매칭 -> movie filter
    if genre_names:
        gq = Q()
        for name in genre_names:
            gq |= Q(name__icontains=name)
        genre_tmdb_ids = list(Genre.objects.filter(gq).values_list("tmdb_id", flat=True))
        if genre_tmdb_ids:
            qs = qs.filter(genres__tmdb_id__in=genre_tmdb_ids).distinct()

    # 키워드 -> title/overview 검색
    if keywords:
        kq = Q()
        for k in keywords:
            kq |= Q(title__icontains=k) | Q(overview__icontains=k)
        qs = qs.filter(kq)

    if min_vote > 0:
        qs = qs.filter(vote_average__gte=min_vote)

    qs = qs.order_by("-vote_average", "-popularity")[:12]

    return Response({
        "answer": data.get("answer") if isinstance(data, dict) else "추천해볼게요.",
        "filters": filters,
        "movies": MovieListSerializer(qs, many=True).data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def genre_recommend(request):
    """
    GET /api/recommends/genres/          -> 장르 목록
    GET /api/recommends/genres/?genre=28 -> 해당 장르 영화
    """
    genre_tmdb_id = request.query_params.get("genre")

    if not genre_tmdb_id:
        genres = Genre.objects.all().order_by("name")
        return Response({
            "genres": [{"tmdb_id": g.tmdb_id, "name": g.name} for g in genres]
        })

    qs = (
        Movie.objects
        .filter(genres__tmdb_id=int(genre_tmdb_id))
        .prefetch_related("genres")
        .order_by("-popularity")[:24]
    )
    return Response({"results": MovieListSerializer(qs, many=True).data})


@api_view(["GET"])
@permission_classes([AllowAny])
def people_recommend(request):
    """
    GET /api/recommends/people/?q=봉준호 -> 검색
    GET /api/recommends/people/         -> 기본 추천(간단 랭킹)
    """
    q = (request.query_params.get("q") or "").strip()
    if q:
        people = Person.objects.filter(name__icontains=q).order_by("name")[:30]
        return Response({"results": PersonSerializer(people, many=True).data})

    # 기본 추천: DB에 쌓인 인물 중 "등장 빈도" 비슷한 걸로(가능하면)
    # MoviePerson 관련 reverse가 기본이면 person.movieperson_set
    try:
        people = (
            Person.objects
            .annotate(credits_count=Count("movieperson_set"))
            .order_by("-credits_count", "name")[:20]
        )
    except Exception:
        people = Person.objects.all().order_by("name")[:20]

    return Response({"results": PersonSerializer(people, many=True).data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_recommend(request):
    """
    GET /api/recommends/users/
    return:
      - top_reviewers: 리뷰 많이 쓴 유저
      - top_liked: 좋아요 많이 받은 유저(리뷰가 받은 like)
      - suggested: (가능하면) 내가 아직 팔로우 안 한 유저 추천
    """
    User = get_user_model()
    me = request.user

    # 리뷰 많이 쓴 유저
    top_reviewers_raw = (
        Review.objects.values("user_id")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:10]
    )
    reviewer_ids = [r["user_id"] for r in top_reviewers_raw]
    reviewer_cnt_map = {r["user_id"]: r["cnt"] for r in top_reviewers_raw}
    reviewers = list(User.objects.filter(id__in=reviewer_ids))

    # 좋아요 많이 받은 유저(ReviewLike 있으면)
    top_liked_users = []
    if ReviewLike is not None:
        top_liked_raw = (
            ReviewLike.objects.values("review__user_id")
            .annotate(cnt=Count("id"))
            .order_by("-cnt")[:10]
        )
        liked_ids = [r["review__user_id"] for r in top_liked_raw]
        liked_cnt_map = {r["review__user_id"]: r["cnt"] for r in top_liked_raw}
        liked_users = list(User.objects.filter(id__in=liked_ids))
        top_liked_users = [
            {"id": u.id, "username": getattr(u, "username", ""), "received_likes": liked_cnt_map.get(u.id, 0)}
            for u in liked_users
        ]

    # suggested: 팔로우 모델이 있으면 "내가 아직 팔로우 안 한 활동 유저" 추천
    suggested = []
    if Follow is not None:
        try:
            following_ids = set(
                Follow.objects.filter(follower=me).values_list("following_id", flat=True)
            )
            base = (
                User.objects.exclude(id=me.id)
                .exclude(id__in=following_ids)
                .annotate(reviews_count=Count("reviews"))
                .order_by("-reviews_count")[:10]
            )
            suggested = [
                {"id": u.id, "username": getattr(u, "username", ""), "reviews_count": getattr(u, "reviews_count", 0)}
                for u in base
            ]
        except Exception:
            suggested = []

    return Response({
        "top_reviewers": [
            {"id": u.id, "username": getattr(u, "username", ""), "reviews_count": reviewer_cnt_map.get(u.id, 0)}
            for u in reviewers
        ],
        "top_liked": top_liked_users,
        "suggested": suggested,
    })
