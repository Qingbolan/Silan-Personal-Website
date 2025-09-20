package projects

import (
	"context"
	"fmt"

	"silan-backend/internal/ent/commentlike"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"entgo.io/ent/dialect/sql"
	"github.com/google/uuid"
	"github.com/zeromicro/go-zero/core/logx"
)

type LikeProjectCommentLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Like/Unlike a comment on project
func NewLikeProjectCommentLogic(ctx context.Context, svcCtx *svc.ServiceContext) *LikeProjectCommentLogic {
	return &LikeProjectCommentLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *LikeProjectCommentLogic) LikeProjectComment(req *types.LikeCommentRequest) (resp *types.LikeCommentResponse, err error) {
	// Validate comment id format
	commentUUID, err := uuid.Parse(req.CommentID)
	if err != nil {
		return nil, fmt.Errorf("invalid comment id")
	}

	// Check if like exists using entgo
	likeQuery := l.svcCtx.DB.CommentLike.Query().Where(commentlike.CommentIDEQ(commentUUID))
	if req.UserIdentityId != "" && req.Fingerprint != "" {
		likeQuery = likeQuery.Where(func(s *sql.Selector) {
			s.Where(sql.Or(
				sql.EQ(s.C("user_identity_id"), req.UserIdentityId),
				sql.EQ(s.C("fingerprint"), req.Fingerprint),
			))
		})
	} else if req.UserIdentityId != "" {
		likeQuery = likeQuery.Where(commentlike.UserIdentityIDEQ(req.UserIdentityId))
	} else if req.Fingerprint != "" {
		likeQuery = likeQuery.Where(commentlike.FingerprintEQ(req.Fingerprint))
	}

	existingLike, err := likeQuery.First(l.ctx)
	exists := err == nil

	if exists {
		// Unlike: delete like and decrement counter using entgo
		err = l.svcCtx.DB.CommentLike.DeleteOne(existingLike).Exec(l.ctx)
		if err != nil {
			return nil, fmt.Errorf("failed to delete like: %v", err)
		}

		// Update comment likes count using entgo
		_, err = l.svcCtx.DB.Comment.UpdateOneID(commentUUID).
			AddLikesCount(-1).
			Save(l.ctx)
		if err != nil {
			return nil, fmt.Errorf("failed to update likes count: %v", err)
		}
	} else {
		// Like: insert like and increment counter using entgo
		likeBuilder := l.svcCtx.DB.CommentLike.Create().
			SetCommentID(commentUUID).
			SetFingerprint(req.Fingerprint)

		if req.UserIdentityId != "" {
			likeBuilder = likeBuilder.SetUserIdentityID(req.UserIdentityId)
		}

		_, err = likeBuilder.Save(l.ctx)
		if err != nil {
			return nil, fmt.Errorf("failed to create like: %v", err)
		}

		// Update comment likes count using entgo
		_, err = l.svcCtx.DB.Comment.UpdateOneID(commentUUID).
			AddLikesCount(1).
			Save(l.ctx)
		if err != nil {
			return nil, fmt.Errorf("failed to update likes count: %v", err)
		}
	}

	// Return current count and status using entgo
	comment, err := l.svcCtx.DB.Comment.Get(l.ctx, commentUUID)
	if err != nil {
		return nil, fmt.Errorf("failed to get comment: %v", err)
	}

	return &types.LikeCommentResponse{LikesCount: comment.LikesCount, IsLikedByUser: !exists}, nil
}
