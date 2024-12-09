from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json

from Notio.models import Note


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Login successful"}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def register_view(request):
    if request.method == "POST":
        try:
            # Cargar el JSON enviado por el cliente
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        # Validar campos obligatorios
        if not username or not password or not email:
            return JsonResponse(
                {"error": "Username, password, and email are required"}, status=400
            )

        # Obtener el modelo de usuario configurado
        User = get_user_model()

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken"}, status=400)

        # Crear el usuario con el modelo personalizado
        try:
            user = User.objects.create_user(
                username=username, password=password, email=email
            )
        except Exception as e:
            return JsonResponse({"error": f"Error creating user: {str(e)}"}, status=500)

        return JsonResponse({"message": "User registered successfully"}, status=201)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def get_user_notes(request):
    """
    Retrieve all notes for the currently logged-in user.
    """
    try:
        # Fetch notes belonging to the current user (creator is the related user field)
        user_notes = Note.objects.filter(creator=request.user).order_by(
            "-creation_date"
        )

        # Convert notes to a list of dictionaries for JSON serialization
        notes_list = [
            {
                "note_id": note.note_id,
                "title": note.title,
                "content": note.content,
                "creation_date": note.creation_date.isoformat(),
                "last_modification": note.last_modification.isoformat(),
                "status": note.status,
            }
            for note in user_notes
        ]

        return JsonResponse({"notes": notes_list, "count": len(notes_list)}, status=200)

    except Exception as e:
        # Handle any unexpected errors
        return JsonResponse(
            {"error": "Failed to retrieve notes", "details": str(e)}, status=500
        )


@login_required
def create_note(request):
    """
    Create a new note for the currently logged-in user.
    """
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)

            # Validate required fields
            if not data.get("title") or not data.get("content"):
                return JsonResponse(
                    {"error": "Title and content are required"}, status=400
                )

            # Create a new note
            new_note = Note.objects.create(
                title=data["title"],
                content=data["content"],
                creation_date=timezone.now(),
                last_modification=timezone.now(),
                status=data.get("status", ""),
                creator=request.user,  # Use the logged-in user
            )

            return JsonResponse(
                {"message": "Note created successfully", "note_id": new_note.note_id},
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        except Exception as e:
            return JsonResponse(
                {"error": "Failed to create note", "details": str(e)}, status=500
            )

    return JsonResponse({"error": "Invalid request method"}, status=405)
