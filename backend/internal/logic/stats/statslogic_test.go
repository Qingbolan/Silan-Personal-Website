package stats

import (
	"context"
	"strings"
	"testing"

	"entgo.io/ent/dialect"
	"silan-backend/internal/ent/comment"
	"silan-backend/internal/ent/contentinteraction"
	"silan-backend/internal/ent/enttest"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	_ "github.com/mattn/go-sqlite3"
)

func newStatsTestContext(t *testing.T) (context.Context, *svc.ServiceContext) {
	t.Helper()
	ctx := context.Background()
	client := enttest.Open(
		t,
		dialect.SQLite,
		"file:"+strings.ReplaceAll(t.Name(), "/", "-")+"?mode=memory&cache=shared&_fk=1",
	)
	return ctx, &svc.ServiceContext{DB: client}
}

func TestSnapshotCarriesCompleteLikerAndModerationDetails(t *testing.T) {
	ctx, svcCtx := newStatsTestContext(t)
	const entityID = "moment-one"

	svcCtx.DB.ContentInteraction.Create().
		SetID("like-one").
		SetEntityType(contentinteraction.EntityTypeMoment).
		SetEntityID(entityID).
		SetKind(contentinteraction.KindLike).
		SetFingerprint("reader-one").
		SetCountryCode("SG").
		SaveX(ctx)
	svcCtx.DB.ContentInteraction.Create().
		SetID("view-without-discussion").
		SetEntityType(contentinteraction.EntityTypeMoment).
		SetEntityID("moment-without-discussion").
		SetKind(contentinteraction.KindView).
		SaveX(ctx)

	svcCtx.DB.Comment.Create().
		SetID("comment-public").
		SetEntityType(comment.EntityTypeMoment).
		SetEntityID(entityID).
		SetAuthorName("Ari").
		SetContent("Public root").
		SetIsApproved(true).
		SaveX(ctx)
	svcCtx.DB.Comment.Create().
		SetID("comment-hidden").
		SetEntityType(comment.EntityTypeMoment).
		SetEntityID(entityID).
		SetParentID("comment-public").
		SetAuthorName("Mei").
		SetContent("Hidden reply").
		SetIsApproved(false).
		SaveX(ctx)

	snapshot, err := NewStatsLogic(ctx, svcCtx).Snapshot()
	if err != nil {
		t.Fatalf("Snapshot: %v", err)
	}
	if !snapshot.InteractionDetailsComplete {
		t.Fatal("snapshot must explicitly declare complete interaction details")
	}
	if len(snapshot.Items) != 2 {
		t.Fatalf("items = %d, want 2", len(snapshot.Items))
	}
	items := make(map[string]types.StatsSnapshotItem, len(snapshot.Items))
	for _, item := range snapshot.Items {
		items[item.Stats.EntityID] = item
	}
	item := items[entityID]
	if item.Stats.Likes != 1 || item.Stats.Comments != 1 {
		t.Fatalf("public stats = %+v, want one like and one public comment", item.Stats)
	}
	if len(item.Likers) != 1 || item.Likers[0].CountryCode != "SG" {
		t.Fatalf("likers = %+v, want the reader identity projection", item.Likers)
	}
	if len(item.Comments) != 1 || len(item.Comments[0].Replies) != 1 {
		t.Fatalf("comments = %+v, want the complete moderation tree", item.Comments)
	}
	if item.Comments[0].Replies[0].IsPublic {
		t.Fatal("hidden reply must retain its moderation state in the private snapshot")
	}
	if items["moment-without-discussion"].Comments == nil {
		t.Fatal("empty comment collections must encode as [] rather than null")
	}
}
