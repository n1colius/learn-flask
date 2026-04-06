"""
=== app/schemas/user.py ===
User schemas for validation and serialization.

Laravel equivalents:
  - UserSchema → UserResource (what gets returned in API responses)
  - UserRegisterSchema → StoreUserRequest (validates registration input)
  - UserLoginSchema → LoginRequest (validates login input)

KEY CONCEPT — Marshmallow Fields:
  fields.String()   → 'string' in Laravel validation
  required=True     → 'required' in Laravel validation
  validate=Length()  → 'min:X|max:Y' in Laravel validation
"""

from app import ma
from marshmallow import fields, validate


class UserSchema(ma.Schema):
    """
    Serialization schema — controls what user data is returned in API responses.

    Laravel equivalent:
      class UserResource extends JsonResource {
          public function toArray($request) {
              return [
                  'id' => $this->id,
                  'name' => $this->name,
                  'email' => $this->email,
                  'created_at' => $this->created_at,
              ];
          }
      }

    Notice: 'password' is NOT included — just like you'd exclude it in Laravel.
    """

    class Meta:
        fields = ('id', 'name', 'email', 'created_at', 'updated_at')


class UserRegisterSchema(ma.Schema):
    """
    Validation schema for user registration.

    Laravel equivalent:
      class StoreUserRequest extends FormRequest {
          public function rules() {
              return [
                  'name' => 'required|string|min:2|max:100',
                  'email' => 'required|email',
                  'password' => 'required|string|min:6',
              ];
          }
      }
    """

    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    email = fields.Email(required=True)  # fields.Email auto-validates email format
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        load_only=True  # load_only = never include in serialized output (like $hidden in Laravel)
    )


class UserLoginSchema(ma.Schema):
    """Validation schema for login."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


# Create reusable instances (like singletons)
user_schema = UserSchema()
users_schema = UserSchema(many=True)  # many=True for serializing a list (like UserResource::collection())
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
