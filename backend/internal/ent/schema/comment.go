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

// Comment holds the schema definition for the unified Comment entity.
type Comment struct {
	ent.Schema
}

// Annotations for the Comment schema.
func (Comment) Annotations() []schema.Annotation {
	return []schema.Annotation{
		entsql.Annotation{Table: "comments"},
	}
}

// Fields of the Comment.
func (Comment) Fields() []ent.Field {
	return []ent.Field{
		field.UUID("id", uuid.UUID{}).
			Default(uuid.New).
			StorageKey("id"),
		field.String("entity_type").
			Comment("Type of entity: 'blog' or 'idea'"),
		field.UUID("entity_id", uuid.UUID{}).
			StorageKey("entity_id").
			Comment("ID of the blog post or idea"),
		field.UUID("parent_id", uuid.UUID{}).
			Optional().
			StorageKey("parent_id"),
		field.String("author_name").
			MaxLen(100).
			NotEmpty(),
		field.String("author_email").
			MaxLen(255).
			NotEmpty(),
		field.String("author_website").
			Optional().
			MaxLen(500),
		field.Text("content").
			NotEmpty(),
		field.String("type").
			Default("general").
			Comment("Type of comment: general, question, suggestion, etc."),
		field.String("referrence_id").
			Optional().
			MaxLen(500),
		field.String("attachment_id").
			Optional().
			MaxLen(500),
		field.Bool("is_approved").
			Default(false),
		field.String("ip_address").
			Optional().
			MaxLen(45),
		field.String("user_agent").
			Optional().
			MaxLen(500),
		field.String("user_identity_id").
			Optional().
			Comment("Link to authenticated user identity if available"),
		field.Int("likes_count").
			Default(0).
			Comment("Number of likes for this comment"),
		field.Time("created_at").
			Default(time.Now).
			Immutable(),
		field.Time("updated_at").
			Default(time.Now).
			UpdateDefault(time.Now),
	}
}

// Edges of the Comment.
func (Comment) Edges() []ent.Edge {
	return []ent.Edge{
		edge.To("parent", Comment.Type).
			Field("parent_id").
			Unique(),
		edge.From("replies", Comment.Type).
			Ref("parent"),
		edge.To("user_identity", UserIdentity.Type).
			Field("user_identity_id").
			Unique(),
	}
}