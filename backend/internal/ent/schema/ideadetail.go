package schema

import (
	"time"

	"entgo.io/ent"
	"entgo.io/ent/dialect/entsql"
	"entgo.io/ent/schema"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
	"github.com/google/uuid"
)

// IdeaDetail holds the schema definition for the IdeaDetail entity.
type IdeaDetail struct {
	ent.Schema
}

// Annotations for the IdeaDetail schema.
func (IdeaDetail) Annotations() []schema.Annotation {
	return []schema.Annotation{
		entsql.Annotation{Table: "idea_details"},
	}
}

// Fields of the IdeaDetail.
func (IdeaDetail) Fields() []ent.Field {
	return []ent.Field{
		field.UUID("id", uuid.UUID{}).
			Default(uuid.New).
			StorageKey("id"),
		field.UUID("idea_id", uuid.UUID{}).
			StorageKey("idea_id"),
		field.Text("progress").
			Optional(),
		field.Text("results").
			Optional(),
		field.Text("references").
			Optional(),
		field.Int("estimated_duration_months").
			Optional(),
		field.Text("required_resources").
			Optional(),
		field.Bool("collaboration_needed").
			Default(false),
		field.Bool("funding_required").
			Default(false),
		field.Float("estimated_budget").
			Optional(),
		field.Time("created_at").
			Default(time.Now).
			Immutable(),
		field.Time("updated_at").
			Default(time.Now).
			UpdateDefault(time.Now),
	}
}

// Edges of the IdeaDetail.
func (IdeaDetail) Edges() []ent.Edge {
	return []ent.Edge{
		edge.From("idea", Idea.Type).
			Ref("details").
			Field("idea_id").
			Required().
			Unique(),
		edge.To("translations", IdeaDetailTranslation.Type),
	}
}
