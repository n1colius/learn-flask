"""
=== app/routes/auth.py ===
Authentication routes: Register, Login, Get Current User.

Laravel equivalent: app/Http/Controllers/AuthController.php
Plus the routes defined in routes/api.php:
  Route::post('/auth/register', [AuthController::class, 'register']);
  Route::post('/auth/login', [AuthController::class, 'login']);
  Route::get('/auth/me', [AuthController::class, 'me'])->middleware('auth:sanctum');

KEY CONCEPT — Blueprints vs Controllers:
  In Laravel, you have a Controller class with methods.
  In Flask, you have a Blueprint with route functions.
  Each function IS a controller method.

  Laravel:
    class AuthController extends Controller {
        public function register(Request $request) { ... }
    }

  Flask:
    @auth_bp.route('/register', methods=['POST'])
    def register():
        ...
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.user import User
from app.schemas.user import user_schema, user_register_schema, user_login_schema

# ── Create Blueprint ────────────────────────────────────────────
# Blueprint = route group. Like Route::prefix('auth')->group(...)
auth_bp = Blueprint('auth', __name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/auth/register
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Laravel equivalent:
      public function register(StoreUserRequest $request) {
          $user = User::create([
              'name' => $request->name,
              'email' => $request->email,
              'password' => Hash::make($request->password),
          ]);
          $token = $user->createToken('auth_token')->plainTextToken;
          return response()->json(['user' => $user, 'token' => $token], 201);
      }
    """

    # ── Step 1: Get JSON body ───────────────────────────────────
    # Laravel: $request->all() or $request->validated()
    # Flask: request.get_json() parses the JSON body
    json_data = request.get_json()

    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    # ── Step 2: Validate the request ────────────────────────────
    # Laravel: This happens automatically with Form Requests.
    # Flask: We call schema.load() which validates AND deserializes.
    # If validation fails, it raises ValidationError (like Laravel's ValidationException).
    try:
        data = user_register_schema.load(json_data)
    except ValidationError as err:
        # err.messages is like $validator->errors() in Laravel
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    # ── Step 3: Check if email already exists ───────────────────
    # Laravel: You'd add 'unique:users' to validation rules.
    # Flask: We check manually (or you could write a custom validator).
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    # ── Step 4: Create the user ─────────────────────────────────
    # Laravel: User::create($validated)
    # Flask: Create instance → add to session → commit
    user = User(
        name=data['name'],
        email=data['email']
    )
    user.set_password(data['password'])  # Hash the password

    # db.session is like a database transaction.
    # In Laravel, Eloquent auto-saves. In Flask, you must explicitly:
    #   1. db.session.add(user)   — stage the insert
    #   2. db.session.commit()    — execute it (like DB::commit())
    db.session.add(user)
    db.session.commit()

    # ── Step 5: Generate JWT token ──────────────────────────────
    # Laravel: $user->createToken('auth')->plainTextToken
    # Flask-JWT: create_access_token(identity=user.id)
    access_token = create_access_token(identity=str(user.id))

    # ── Step 6: Return response ─────────────────────────────────
    # Laravel: return response()->json([...], 201);
    # Flask: return jsonify({...}), 201
    return jsonify({
        'message': 'User registered successfully',
        'user': user_schema.dump(user),  # .dump() serializes the object (like UserResource)
        'access_token': access_token
    }), 201


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/auth/login
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login and receive a JWT token.

    Laravel equivalent:
      public function login(LoginRequest $request) {
          if (!Auth::attempt($request->validated())) {
              return response()->json(['error' => 'Invalid credentials'], 401);
          }
          $token = auth()->user()->createToken('auth_token')->plainTextToken;
          return response()->json(['token' => $token]);
      }
    """

    json_data = request.get_json()

    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = user_login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    # Find user by email
    # Laravel: User::where('email', $request->email)->first()
    # Flask-SQLAlchemy: User.query.filter_by(email=...).first()
    user = User.query.filter_by(email=data['email']).first()

    # Check credentials
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Generate token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': 'Login successful',
        'user': user_schema.dump(user),
        'access_token': access_token
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/auth/me
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@auth_bp.route('/me', methods=['GET'])
@jwt_required()  # ← This is like Laravel's ->middleware('auth:sanctum')
def me():
    """
    Get the currently authenticated user's profile.

    Laravel equivalent:
      Route::middleware('auth:sanctum')->get('/me', function (Request $request) {
          return new UserResource($request->user());
      });

    KEY CONCEPT — @jwt_required() decorator:
      In Laravel, middleware is defined in routes or controller constructor.
      In Flask, decorators serve the same purpose.

      Laravel:  Route::middleware('auth:sanctum')->get(...)
      Flask:    @jwt_required()
                def my_route():

      A decorator is a function that wraps another function to add behavior.
      It's exactly like middleware — runs before your function, can block access.
    """

    # get_jwt_identity() returns the user ID from the JWT token
    # Laravel equivalent: auth()->id() or $request->user()->id
    current_user_id = get_jwt_identity()

    # Find the user — Laravel: User::findOrFail($id)
    user = User.query.get(int(current_user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'user': user_schema.dump(user)
    }), 200
