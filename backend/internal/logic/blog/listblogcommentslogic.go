package blog

import (
	"context"
	"database/sql"
	"time"

	"silan-backend/internal/ent/blogcomment"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/google/uuid"
	"github.com/zeromicro/go-zero/core/logx"
)

type ListBlogCommentsLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// List comments for a blog post
func NewListBlogCommentsLogic(ctx context.Context, svcCtx *svc.ServiceContext) *ListBlogCommentsLogic {
	return &ListBlogCommentsLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *ListBlogCommentsLogic) ListBlogComments(req *types.BlogCommentListRequest) (resp *types.BlogCommentListResponse, err error) {
	postID, err := uuid.Parse(req.ID)
	if err != nil {
		return nil, err
	}

	list, err := l.svcCtx.DB.BlogComment.
		Query().
		Where(blogcomment.BlogPostIDEQ(postID)).
		Order(blogcomment.ByCreatedAt()).
		All(l.ctx)
	if err != nil {
		return nil, err
	}

	// cache avatar lookups per email within this request
	avatarCache := map[string]string{}

	lookupAvatar := func(email string) string {
		if email == "" {
			return ""
		}
		if v, ok := avatarCache[email]; ok {
			return v
		}
		var (
			url sql.NullString
			drv = l.svcCtx.Config.Database.Driver
		)
		if drv == "postgres" || drv == "postgresql" {
			_ = l.svcCtx.RawDB.QueryRowContext(l.ctx,
				"SELECT avatar_url FROM user_identities WHERE email = $1 ORDER BY updated_at DESC LIMIT 1",
				email,
			).Scan(&url)
		} else {
			_ = l.svcCtx.RawDB.QueryRowContext(l.ctx,
				"SELECT avatar_url FROM user_identities WHERE email = ? ORDER BY updated_at DESC LIMIT 1",
				email,
			).Scan(&url)
		}
		if url.Valid {
			avatarCache[email] = url.String
			return url.String
		}
		avatarCache[email] = ""
		return ""
	}

	comments := make([]types.BlogCommentData, 0, len(list))
	for _, c := range list {
		comments = append(comments, types.BlogCommentData{
			ID:              c.ID.String(),
			BlogPostID:      c.BlogPostID.String(),
			AuthorName:      c.AuthorName,
			AuthorAvatarURL: lookupAvatar(c.AuthorEmail),
			Content:         c.Content,
			CreatedAt:       c.CreatedAt.Format(time.RFC3339),
		})
	}

	return &types.BlogCommentListResponse{Comments: comments, Total: len(comments)}, nil
}

