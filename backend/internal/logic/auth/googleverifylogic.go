package auth

import (
	"context"
	"crypto/md5"
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

type GoogleVerifyLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Verify Google ID token and upsert identity
func NewGoogleVerifyLogic(ctx context.Context, svcCtx *svc.ServiceContext) *GoogleVerifyLogic {
	return &GoogleVerifyLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *GoogleVerifyLogic) GoogleVerify(req *types.GoogleVerifyRequest) (resp *types.GoogleVerifyResponse, err error) {
	if req.IdToken == "" {
		return nil, fmt.Errorf("id_token is required")
	}

	// Verify Google ID token
	oauth2Service, err := oauth2.NewService(l.ctx, option.WithoutAuthentication())
	if err != nil {
		l.Errorf("Failed to create OAuth2 service: %v", err)
		return nil, fmt.Errorf("authentication service unavailable")
	}

	tokenInfo, err := oauth2Service.Tokeninfo().IdToken(req.IdToken).Do()
	if err != nil {
		l.Errorf("Failed to verify Google ID token: %v", err)
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

	if tokenInfo.Email == "" {
		return nil, fmt.Errorf("email not provided")
	}

	// Generate or get existing user identity
	externalID := tokenInfo.UserId
	if externalID == "" {
		// Fallback to email hash if user ID not available
		hash := md5.Sum([]byte(tokenInfo.Email))
		externalID = fmt.Sprintf("email:%x", hash)
	}

	// Upsert user identity
	userIdentity, err := l.upsertUserIdentity("google", externalID, tokenInfo)
	if err != nil {
		l.Errorf("Failed to upsert user identity: %v", err)
		return nil, fmt.Errorf("failed to process user identity")
	}

	return &types.GoogleVerifyResponse{
		ID:        userIdentity.ID,
		Email:     userIdentity.Email,
		Name:      userIdentity.DisplayName,
		AvatarURL: userIdentity.AvatarURL,
		Provider:  userIdentity.Provider,
		Verified:  userIdentity.Verified,
	}, nil
}

func (l *GoogleVerifyLogic) upsertUserIdentity(provider, externalID string, tokenInfo *oauth2.Tokeninfo) (*ent.UserIdentity, error) {
	// Try to find existing identity
	existing, err := l.svcCtx.DB.UserIdentity.
		Query().
		Where(
			useridentity.ProviderEQ(provider),
			useridentity.ExternalIDEQ(externalID),
		).
		First(l.ctx)

	if err == nil {
		// Update existing identity
		updateBuilder := l.svcCtx.DB.UserIdentity.
			UpdateOne(existing).
			SetUpdatedAt(time.Now())

		if tokenInfo.Email != "" {
			updateBuilder = updateBuilder.SetEmail(tokenInfo.Email)
		}
		updateBuilder = updateBuilder.SetVerified(tokenInfo.VerifiedEmail)

		return updateBuilder.Save(l.ctx)
	}

	// Create new identity
	createBuilder := l.svcCtx.DB.UserIdentity.
		Create().
		SetID(l.generateUserID()).
		SetProvider(provider).
		SetExternalID(externalID)

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

func (l *GoogleVerifyLogic) generateUserID() string {
	// Generate a user ID that starts with 'u_' followed by UUID
	uuid := uuid.New()
	return "u_" + strings.ReplaceAll(uuid.String(), "-", "")
}
