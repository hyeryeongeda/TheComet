# backend/reviews/serializers.py
from rest_framework import serializers
from .models import Review


class ReviewUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["content", "watched", "rating"]

    def validate(self, attrs):
        watched = attrs.get("watched", None)
        rating = attrs.get("rating", None)
        content = (attrs.get("content") or "").strip()

        if watched is not True:
            raise serializers.ValidationError("리뷰 작성은 '봤어요' 체크가 필요합니다.")
        if rating is None:
            raise serializers.ValidationError("별점은 필수입니다.")
        if not (1 <= rating <= 5):
            raise serializers.ValidationError("별점은 1~5 사이여야 합니다.")
        if not content:
            raise serializers.ValidationError("한줄평을 입력해 주세요.")
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    # ✅ DB annotate는 likes_count로 받고(views에서 annotate(likes_count=Count("likes")))
    likes_count = serializers.IntegerField(read_only=True)

    # ✅ 프론트는 like_count를 쓰고 있으니까 그대로 내려주되, 실제 값은 likes_count에서 꺼내서 내려줌
    like_count = serializers.SerializerMethodField()

    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "movie",
            "user",
            "content",
            "watched",
            "rating",
            "likes_count",
            "like_count",
            "is_liked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "movie",
            "user",
            "likes_count",
            "created_at",
            "updated_at",
        ]

    def get_like_count(self, obj):
        # annotate가 있으면 그 값을 우선 사용
        if hasattr(obj, "likes_count") and obj.likes_count is not None:
            return obj.likes_count
        # annotate가 없으면 실제 relation count로 fallback
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(id=request.user.id).exists()


class RecentReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    likes_count = serializers.IntegerField(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    # ✅ Home 카드 이동용 유지
    movie_tmdb_id = serializers.IntegerField(source="movie.tmdb_id", read_only=True)
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "content",
            "rating",
            "likes_count",
            "like_count",
            "is_liked",
            "movie_tmdb_id",
            "movie_title",
            "created_at",
        ]

    def get_like_count(self, obj):
        if hasattr(obj, "likes_count") and obj.likes_count is not None:
            return obj.likes_count
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(id=request.user.id).exists()
