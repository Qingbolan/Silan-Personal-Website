package ideas

import (
	"context"
	"fmt"
	"strings"

	"silan-backend/internal/ent"
	"silan-backend/internal/ent/comment"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/google/uuid"
	"github.com/zeromicro/go-zero/core/logx"
)

type DeleteCommentLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Delete a comment (fingerprint or owner identity required)
func NewDeleteIdeaCommentLogic(ctx context.Context, svcCtx *svc.ServiceContext) *DeleteCommentLogic {
	return &DeleteCommentLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *DeleteCommentLogic) DeleteComment(req *types.DeleteIdeaCommentRequest) error {
	commentUUID, err := uuid.Parse(req.CommentID)
	if err != nil {
		return fmt.Errorf("invalid comment id")
	}

	// Load comment meta using entgo
	comment, err := l.svcCtx.DB.Comment.Query().Where(comment.IDEQ(commentUUID), comment.EntityTypeEQ("idea")).Only(l.ctx)
	if err != nil {
		if ent.IsNotFound(err) {
			return fmt.Errorf("comment not found")
		}
		return err
	}

	// Authorization: identity or fingerprint match in user_agent
	authorized := false
	if req.UserIdentityId != "" && comment.UserIdentityID != "" && req.UserIdentityId == comment.UserIdentityID {
		authorized = true
	}
	if !authorized && req.Fingerprint != "" && strings.Contains(comment.UserAgent, "fp:"+req.Fingerprint) {
		authorized = true
	}
	if !authorized {
		return fmt.Errorf("forbidden: insufficient permissions to delete this comment")
	}

	// Recursive delete
	return l.deleteWithReplies(req.CommentID)
}

func (l *DeleteCommentLogic) deleteWithReplies(commentID string) error {
	commentUUID, err := uuid.Parse(commentID)
	if err != nil {
		return err
	}

	// Find replies using entgo
	replies, err := l.svcCtx.DB.Comment.Query().
		Where(comment.ParentIDEQ(commentUUID)).
		All(l.ctx)
	if err != nil {
		return err
	}

	// Recursively delete replies
	for _, reply := range replies {
		if err := l.deleteWithReplies(reply.ID.String()); err != nil {
			return err
		}
	}

	// Delete self using entgo
	err = l.svcCtx.DB.Comment.DeleteOneID(commentUUID).Exec(l.ctx)
	return err
}


