package blog

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"sort"
	"strings"

	"silan-backend/internal/ent"
	"silan-backend/internal/ent/itempart"
	"silan-backend/internal/logic/engagement"
	"silan-backend/internal/siteidentity"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"
)

// resolveLang normalizes an empty language to the default ("en").
func resolveLang(lang string) string {
	if lang == "" {
		return "en"
	}
	return lang
}

// blogDetailData is the single projection for both slug and ID detail
// transports. Keeping it here prevents the two public routes from drifting in
// content IDs, actor state, author metadata, or language fallback.
func blogDetailData(
	ctx context.Context,
	svcCtx *svc.ServiceContext,
	post *ent.BlogPost,
	language string,
	userIdentityID string,
	fingerprint string,
) (*types.BlogData, error) {
	tags, err := svcCtx.ContentTags.Lookup(ctx, "blog", post.ID)
	if err != nil {
		return nil, err
	}

	title := post.Title
	excerpt := post.Excerpt
	if tr := pickBlogTranslation(post.Edges.Translations, language); tr != nil {
		if tr.Title != "" {
			title = tr.Title
		}
		if tr.Excerpt != "" {
			excerpt = tr.Excerpt
		}
	}
	body := post.Content
	if synced := blogBody(ctx, svcCtx, post.ID, language); synced != "" {
		body = synced
	}

	author, err := siteidentity.OwnerName(ctx, svcCtx.DB, language)
	if err != nil {
		return nil, err
	}

	counts, err := engagement.BlogCount(ctx, svcCtx.DB, post.ID)
	if err != nil {
		return nil, err
	}
	liked, err := engagement.IsBlogLiked(ctx, svcCtx.DB, post.ID, userIdentityID, fingerprint)
	if err != nil {
		return nil, err
	}
	likers, err := engagement.ContentLikers(ctx, svcCtx.DB, "blog", post.ID, 24)
	if err != nil {
		return nil, err
	}

	readTime := ""
	if post.ReadingTimeMinutes > 0 {
		readTime = fmt.Sprintf("%d min read", post.ReadingTimeMinutes)
	}
	seriesID := post.SeriesID
	seriesTitle := ""
	if seriesID != "" {
		seriesTitle = seriesID
	}

	return &types.BlogData{
		ID:                post.ID,
		Title:             title,
		Slug:              post.Slug,
		Author:            author,
		PublishDate:       post.PublishedAt,
		UpdatedAt:         post.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
		ReadTime:          readTime,
		Category:          post.CategoryID,
		Tags:              tags,
		Content:           []types.BlogContent{{Type: "text", Content: body, ID: post.ID + "-content"}},
		Likes:             int64(counts.Likes),
		IsLikedByUser:     liked,
		Likers:            UpdateLikers(likers),
		Views:             int64(counts.Views),
		Summary:           excerpt,
		FeaturedImageURL:  blogFeaturedImageURL(post, language),
		FeaturedImageURLs: blogFeaturedImageURLs(post),
		ProjectName:       post.ProjectName,
		PublicationVenue:  post.PublicationVenue,
		ProjectURL:        post.ProjectURL,
		ExternalResources: parseBlogResources(post.ExternalResources),
		Type:              string(post.ContentType),
		SeriesID:          seriesID,
		SeriesSlug:        seriesID,
		SeriesTitle:       seriesTitle,
		EpisodeNumber:     post.SeriesOrder,
	}, nil
}

// parseBlogResources turns the source-authored JSON projection into the
// public typed contract. Malformed or unsafe rows are omitted individually so
// one stale attachment never prevents the article itself from loading.
func parseBlogResources(raw string) []types.BlogResource {
	if strings.TrimSpace(raw) == "" {
		return nil
	}
	var resources []types.BlogResource
	if err := json.Unmarshal([]byte(raw), &resources); err != nil {
		return nil
	}
	filtered := make([]types.BlogResource, 0, len(resources))
	seen := make(map[string]struct{}, len(resources))
	for _, resource := range resources {
		resource.Kind = strings.TrimSpace(resource.Kind)
		resource.Label = strings.TrimSpace(resource.Label)
		resource.URL = strings.TrimSpace(resource.URL)
		parsed, err := url.ParseRequestURI(resource.URL)
		if err != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") || parsed.Host == "" {
			continue
		}
		if _, exists := seen[resource.URL]; exists {
			continue
		}
		seen[resource.URL] = struct{}{}
		filtered = append(filtered, resource)
	}
	if len(filtered) == 0 {
		return nil
	}
	return filtered
}

// blogFeaturedImageURLs exposes only explicitly authored locale variants.
// The main-table value is a migration fallback, not a language assignment.
func blogFeaturedImageURLs(post *ent.BlogPost) map[string]string {
	images := make(map[string]string)
	for _, translation := range post.Edges.Translations {
		if translation.FeaturedImageURL != "" {
			images[translation.LanguageCode] = translation.FeaturedImageURL
		}
	}
	if len(images) == 0 {
		return nil
	}
	return images
}

// blogFeaturedImageURL resolves the cover for one response language. The
// requested language wins, then English, then the legacy shared cover. A
// final deterministic translation fallback keeps older partial datasets
// usable without assigning the wrong locale when a shared cover exists.
func blogFeaturedImageURL(post *ent.BlogPost, language string) string {
	byLanguage := blogFeaturedImageURLs(post)
	requested := resolveLang(language)
	if image := byLanguage[requested]; image != "" {
		return image
	}
	if image := byLanguage["en"]; image != "" {
		return image
	}
	if post.FeaturedImageURL != "" {
		return post.FeaturedImageURL
	}

	languages := make([]string, 0, len(byLanguage))
	for languageCode := range byLanguage {
		languages = append(languages, languageCode)
	}
	sort.Strings(languages)
	if len(languages) > 0 {
		return byLanguage[languages[0]]
	}
	return ""
}

// pickBlogTranslation selects the best blog translation for a language:
// the requested language, then "en", then the first available. It returns
// nil when there are no translations.
func pickBlogTranslation(trs []*ent.BlogPostTranslation, lang string) *ent.BlogPostTranslation {
	by := func(code string) *ent.BlogPostTranslation {
		for _, t := range trs {
			if t.LanguageCode == code {
				return t
			}
		}
		return nil
	}
	if t := by(resolveLang(lang)); t != nil {
		return t
	}
	if t := by("en"); t != nil {
		return t
	}
	if len(trs) > 0 {
		return trs[0]
	}
	return nil
}

// blogBody fetches a blog post's prose body for a language. The content
// engine stores the body in item_part_translation (keyed by the `body`
// item_part of the owning blog Item), not in blog_posts.content — so the
// detail endpoints read it here. It prefers the requested language, then
// "en", then any. Returns "" when the post has no synced body part.
func blogBody(ctx context.Context, svcCtx *svc.ServiceContext, postID, lang string) string {
	part, err := svcCtx.DB.ItemPart.Query().
		Where(
			itempart.EntityTypeEQ(itempart.EntityTypeBlog),
			itempart.EntityIDEQ(postID),
			itempart.Role("body"),
		).
		WithTranslations().
		First(ctx)
	if err != nil || part == nil {
		return ""
	}
	trs := part.Edges.Translations
	by := func(code string) string {
		for _, t := range trs {
			if t.LanguageCode == code && t.Body != "" {
				return t.Body
			}
		}
		return ""
	}
	if b := by(resolveLang(lang)); b != "" {
		return b
	}
	if b := by("en"); b != "" {
		return b
	}
	for _, t := range trs {
		if t.Body != "" {
			return t.Body
		}
	}
	return ""
}
