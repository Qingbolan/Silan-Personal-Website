package blog

import (
	"context"
	"fmt"
	"strings"

	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/google/uuid"
	"github.com/zeromicro/go-zero/core/logx"
)

type DeleteBlogCommentLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Delete a comment (fingerprint required)
func NewDeleteBlogCommentLogic(ctx context.Context, svcCtx *svc.ServiceContext) *DeleteBlogCommentLogic {
	return &DeleteBlogCommentLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *DeleteBlogCommentLogic) DeleteBlogComment(req *types.DeleteBlogCommentRequest) error {
	cid, err := uuid.Parse(req.CommentID)
	if err != nil {
		return err
	}

	c, err := l.svcCtx.DB.BlogComment.Get(l.ctx, cid)
	if err != nil {
		return err
	}

	// Check authorization
	authorized := false

	// Method 1: Check fingerprint for anonymous users
	if req.Fingerprint != "" && strings.Contains(c.UserAgent, "fp:"+req.Fingerprint) {
		authorized = true
	}

	// Method 2: Placeholder for user ownership verification
	if !authorized {
		// TODO: verify ownership via user identity if available
	}

	if !authorized {
		return fmt.Errorf("forbidden: insufficient permissions to delete this comment")
	}

	return l.svcCtx.DB.BlogComment.DeleteOneID(cid).Exec(l.ctx)
}

// Helper function to verify user identity (for future use)
func (l *DeleteBlogCommentLogic) verifyUserOwnership(userIdentityId string, comment interface{}) bool {
	// This would check if the authenticated user owns the comment
	// Implementation depends on your authentication middleware
	return false
}

