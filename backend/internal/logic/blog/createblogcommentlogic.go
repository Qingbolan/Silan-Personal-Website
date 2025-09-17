package blog

import (
	"context"
	"database/sql"
	"fmt"
	"strings"
	"time"

	"silan-backend/internal/ent"
	"silan-backend/internal/ent/useridentity"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/google/uuid"
	"github.com/zeromicro/go-zero/core/logx"
	"google.golang.org/api/oauth2/v2"
	"google.golang.org/api/option"
)

type CreateBlogCommentLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Create a comment for a blog post
func NewCreateBlogCommentLogic(ctx context.Context, svcCtx *svc.ServiceContext) *CreateBlogCommentLogic {
	return &CreateBlogCommentLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *CreateBlogCommentLogic) CreateBlogComment(req *types.CreateBlogCommentRequest) (resp *types.BlogCommentData, err error) {
	if req.Content == "" {
		return nil, fmt.Errorf("content is required")
	}

	postID, err := uuid.Parse(req.ID)
	if err != nil {
		return nil, err
	}

	// Handle authentication
	var userIdentity *ent.UserIdentity
	var authorName, authorEmail, avatarURL string

	// If user provides an ID token, verify and get user info
	if req.IdToken != "" {
		userIdentity, err = l.verifyAndGetUser(req.IdToken)
		if err != nil {
			return nil, fmt.Errorf("token verification failed: %v", err)
		}
		authorName = userIdentity.DisplayName
		authorEmail = userIdentity.Email
		avatarURL = userIdentity.AvatarURL
	} else if req.UserIdentityId != "" {
		// If user provides identity ID, validate it exists
		userIdentity, err = l.svcCtx.DB.UserIdentity.Get(l.ctx, req.UserIdentityId)
		if err != nil {
			return nil, fmt.Errorf("invalid user identity")
		}
		authorName = userIdentity.DisplayName
		authorEmail = userIdentity.Email
		avatarURL = userIdentity.AvatarURL
	} else {
		// Anonymous user - require name and email
		if req.AuthorName == "" {
			return nil, fmt.Errorf("author_name is required for anonymous comments")
		}
		if req.AuthorEmail == "" {
			return nil, fmt.Errorf("author_email is required for anonymous comments")
		}
		if !strings.Contains(req.AuthorEmail, "@") || len(req.AuthorEmail) < 5 {
			return nil, fmt.Errorf("author_email format is invalid")
		}
		authorName = req.AuthorName
		authorEmail = req.AuthorEmail
		// Try to get avatar from existing user identities
		avatarURL = l.lookupAvatarByEmail(req.AuthorEmail)
	}

	// Create comment
	createBuilder := l.svcCtx.DB.BlogComment.Create().
		SetBlogPostID(postID).
		SetAuthorName(authorName).
		SetAuthorEmail(authorEmail).
		SetContent(req.Content).
		SetIsApproved(true).
		SetUserAgent("fp:" + req.Fingerprint)

	if userIdentity != nil {
		createBuilder = createBuilder.SetUserIdentityID(userIdentity.ID)
	}

	c, err := createBuilder.Save(l.ctx)
	if err != nil {
		return nil, err
	}

	return &types.BlogCommentData{
		ID:              c.ID.String(),
		BlogPostID:      c.BlogPostID.String(),
		AuthorName:      c.AuthorName,
		AuthorAvatarURL: avatarURL,
		Content:         c.Content,
		CreatedAt:       c.CreatedAt.Format(time.RFC3339),
	}, nil
}

func (l *CreateBlogCommentLogic) verifyAndGetUser(idToken string) (*ent.UserIdentity, error) {
	// Verify Google ID token
	oauth2Service, err := oauth2.NewService(l.ctx, option.WithoutAuthentication())
	if err != nil {
		return nil, fmt.Errorf("authentication service unavailable")
	}

	tokenInfo, err := oauth2Service.Tokeninfo().IdToken(idToken).Do()
	if err != nil {
		return nil, fmt.Errorf("invalid token")
	}
	// Optional audience (client id) check if configured
	if l.svcCtx.Config.Auth.GoogleClientID != "" {
		if tokenInfo.Audience != l.svcCtx.Config.Auth.GoogleClientID {
			return nil, fmt.Errorf("invalid audience")
		}
	}

	if !tokenInfo.VerifiedEmail {
		return nil, fmt.Errorf("email not verified")
	}

	// Find or create user identity
	existingUser, err := l.svcCtx.DB.UserIdentity.
		Query().
		Where(
			useridentity.ProviderEQ("google"),
			useridentity.ExternalIDEQ(tokenInfo.UserId),
		).
		First(l.ctx)

	if err == nil {
		return existingUser, nil
	}

	// Create new identity if not found
	createBuilder := l.svcCtx.DB.UserIdentity.
		Create().
		SetID(l.generateUserID()).
		SetProvider("google").
		SetExternalID(tokenInfo.UserId)

	if tokenInfo.Email != "" {
		createBuilder = createBuilder.SetEmail(tokenInfo.Email)
	}
	// Generate display name from email
	if tokenInfo.Email != "" {
		emailParts := strings.Split(tokenInfo.Email, "@")
		if len(emailParts) > 0 {
			createBuilder = createBuilder.SetDisplayName(emailParts[0])
		}
	}
	// Note: OAuth2 v2 API doesn't provide picture field, skip for now
	createBuilder = createBuilder.SetVerified(tokenInfo.VerifiedEmail)

	return createBuilder.Save(l.ctx)
}

func (l *CreateBlogCommentLogic) lookupAvatarByEmail(email string) string {
	var avatar sql.NullString
	drv := l.svcCtx.Config.Database.Driver
	if drv == "postgres" || drv == "postgresql" {
		_ = l.svcCtx.RawDB.QueryRowContext(l.ctx,
			"SELECT avatar_url FROM user_identities WHERE email = $1 ORDER BY updated_at DESC LIMIT 1",
			email,
		).Scan(&avatar)
	} else {
		_ = l.svcCtx.RawDB.QueryRowContext(l.ctx,
			"SELECT avatar_url FROM user_identities WHERE email = ? ORDER BY updated_at DESC LIMIT 1",
			email,
		).Scan(&avatar)
	}
	if avatar.Valid {
		return avatar.String
	}
	return ""
}

func (l *CreateBlogCommentLogic) generateUserID() string {
	uuid := uuid.New()
	return "u_" + strings.ReplaceAll(uuid.String(), "-", "")
}
