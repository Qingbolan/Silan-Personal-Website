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

func (l *ListBlogCommentsLogic) ListBlogComments(req *types.BlogCommentListRequest, clientIP, userAgent string) (resp *types.BlogCommentListResponse, err error) {
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

	// Build comment tree structure
	commentMap := make(map[string]*types.BlogCommentData)
	var rootCommentIDs []string

	// First pass: create all comment objects
	for _, c := range list {
		parentIDStr := ""
		// Check if ParentID is not zero value (empty UUID)
		if c.ParentID != (uuid.UUID{}) {
			parentIDStr = c.ParentID.String()
		}

		userIdentityIDStr := ""
		if c.UserIdentityID != "" {
			userIdentityIDStr = c.UserIdentityID
		}

		comment := types.BlogCommentData{
			ID:             c.ID.String(),
			BlogPostID:     c.BlogPostID.String(),
			ParentID:       parentIDStr,
			AuthorName:     c.AuthorName,
			AuthorAvatarURL: lookupAvatar(c.AuthorEmail),
			Content:        c.Content,
			CreatedAt:      c.CreatedAt.Format(time.RFC3339),
			UserIdentityID: userIdentityIDStr,
			Replies:        []types.BlogCommentData{},
		}
		commentMap[c.ID.String()] = &comment

		// Track root comments
		if c.ParentID == (uuid.UUID{}) {
			rootCommentIDs = append(rootCommentIDs, c.ID.String())
		}
	}

	// Second pass: build tree structure
	for _, c := range list {
		if c.ParentID != (uuid.UUID{}) {
			// This is a reply - add to parent's replies
			parentID := c.ParentID.String()
			if parent, exists := commentMap[parentID]; exists {
				comment := commentMap[c.ID.String()]
				parent.Replies = append(parent.Replies, *comment)
			}
		}
	}

	// Third pass: build final root comments array with populated replies
	var rootComments []types.BlogCommentData
	for _, rootID := range rootCommentIDs {
		if rootComment, exists := commentMap[rootID]; exists {
			rootComments = append(rootComments, *rootComment)
		}
	}

	// Log analytics data (optional - could be moved to a separate analytics service)
	l.Infof("Returned %d comments (%d root, %d total) for post %s to IP %s",
		len(rootComments), len(rootComments), len(list), req.ID, clientIP)

	return &types.BlogCommentListResponse{Comments: rootComments, Total: len(list)}, nil
}

