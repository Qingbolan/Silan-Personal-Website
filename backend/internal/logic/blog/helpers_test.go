package blog

import (
	"testing"

	"silan-backend/internal/ent"
)

func TestBlogFeaturedImageURLPrefersRequestedLanguage(t *testing.T) {
	post := blogPostWithCovers(
		"/media/shared.png",
		map[string]string{
			"en": "/media/cover-en.png",
			"zh": "/media/cover-zh.png",
		},
	)

	if got := blogFeaturedImageURL(post, "zh"); got != "/media/cover-zh.png" {
		t.Fatalf("zh cover = %q, want localized cover", got)
	}
	if got := blogFeaturedImageURL(post, "en"); got != "/media/cover-en.png" {
		t.Fatalf("en cover = %q, want localized cover", got)
	}
}

func TestBlogFeaturedImageURLFallsBackWithoutInventingLocale(t *testing.T) {
	post := blogPostWithCovers(
		"/media/shared.png",
		map[string]string{"zh": "/media/cover-zh.png"},
	)

	if got := blogFeaturedImageURL(post, "en"); got != "/media/shared.png" {
		t.Fatalf("en cover = %q, want legacy shared cover", got)
	}
}

func TestBlogFeaturedImageURLsContainsOnlyAuthoredVariants(t *testing.T) {
	post := blogPostWithCovers(
		"/media/shared.png",
		map[string]string{
			"en": "/media/cover-en.png",
			"zh": "",
		},
	)

	images := blogFeaturedImageURLs(post)
	if len(images) != 1 || images["en"] != "/media/cover-en.png" {
		t.Fatalf("localized cover map = %#v", images)
	}
}

func TestParseBlogResourcesKeepsOrderedSafeUniqueLinks(t *testing.T) {
	resources := parseBlogResources(`[
		{"kind":"website","label":"Project","url":"https://gem-bench.org/"},
		{"kind":"github","label":"Code","url":"https://github.com/Generative-Engine-Marketing/GEM-Bench"},
		{"kind":"duplicate","url":"https://gem-bench.org/"},
		{"kind":"unsafe","url":"javascript:alert(1)"}
	]`)
	if len(resources) != 2 {
		t.Fatalf("resources = %#v, want two safe unique links", resources)
	}
	if resources[0].Kind != "website" || resources[1].Kind != "github" {
		t.Fatalf("resource order = %#v", resources)
	}
}

func TestParseBlogResourcesRejectsMalformedJSON(t *testing.T) {
	if resources := parseBlogResources(`not-json`); resources != nil {
		t.Fatalf("malformed resources = %#v, want nil", resources)
	}
}

func blogPostWithCovers(shared string, covers map[string]string) *ent.BlogPost {
	translations := make([]*ent.BlogPostTranslation, 0, len(covers))
	for language, cover := range covers {
		translations = append(translations, &ent.BlogPostTranslation{
			LanguageCode:     language,
			FeaturedImageURL: cover,
		})
	}
	return &ent.BlogPost{
		FeaturedImageURL: shared,
		Edges: ent.BlogPostEdges{
			Translations: translations,
		},
	}
}
