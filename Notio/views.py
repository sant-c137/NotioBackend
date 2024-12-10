from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from django.contrib.auth import logout
from django.http import JsonResponse


from django.shortcuts import get_object_or_404
from .models import Note, SharedNotes
from django.contrib.auth.models import User
import json


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


def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully"}, status=200)


@csrf_exempt
def register_view(request):
    if request.method == "POST":
        try:

            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if not username or not password or not email:
            return JsonResponse(
                {"error": "Username, password, and email are required"}, status=400
            )

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken"}, status=400)

        try:
            user = User.objects.create_user(
                username=username, password=password, email=email
            )
        except Exception as e:
            return JsonResponse({"error": f"Error creating user: {str(e)}"}, status=500)

        return JsonResponse({"message": "User registered successfully"}, status=201)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def check_session(request):
    return JsonResponse(
        {"authenticated": True, "username": request.user.username}, status=200
    )


@login_required
def get_user_notes(request):
    """
    Retrieve all notes for the currently logged-in user.
    """
    try:

        user_notes = Note.objects.filter(creator=request.user).order_by(
            "-creation_date"
        )

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

            data = json.loads(request.body)

            if not data.get("title") or not data.get("content"):
                return JsonResponse(
                    {"error": "Title and content are required"}, status=400
                )

            new_note = Note.objects.create(
                title=data["title"],
                content=data["content"],
                creation_date=timezone.now(),
                last_modification=timezone.now(),
                status=data.get("status", ""),
                creator=request.user,
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


@login_required
def delete_user_note(request, note_id):
    """
    Delete a note for the currently logged-in user.
    """
    try:

        note = Note.objects.filter(note_id=note_id, creator=request.user).first()

        if not note:
            return JsonResponse(
                {"error": "Note not found or not authorized to delete."}, status=404
            )

        note.delete()

        return JsonResponse({"message": "Note deleted successfully."}, status=200)

    except Exception as e:

        return JsonResponse(
            {"error": "Failed to delete note", "details": str(e)}, status=500
        )


@login_required
def edit_note(request, note_id):
    """
    Edit a note for the currently logged-in user.
    """
    try:
        note = Note.objects.get(note_id=note_id, creator=request.user)
        data = json.loads(request.body)

        note.title = data.get("title", note.title)
        note.content = data.get("content", note.content)
        note.status = data.get("status", note.status)
        note.last_modification = timezone.now()
        note.save()

        return JsonResponse({"message": "Note updated successfully"}, status=200)
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)
    except Exception as e:
        return JsonResponse(
            {"error": "Failed to update note", "details": str(e)}, status=500
        )


@login_required
def share_note(request):
    """
    Share a note with another user, granting 'view' or 'edit' permissions.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        body = json.loads(request.body)
        print("Parsed body:", body)
        note_id = body.get("note_id")
        shared_user_email = body.get("shared_user_email")
        permission = body.get("permission")

        if not note_id or not shared_user_email or not permission:
            return JsonResponse(
                {"error": "note_id, shared_user_email, y permission son requeridos."},
                status=400,
            )

        if permission not in ["view", "edit"]:
            return JsonResponse({"error": "Tipo de permiso inválido."}, status=400)

        note = get_object_or_404(Note, pk=note_id, creator=request.user)
        print("Note retrieved:", note)

        shared_user = get_object_or_404(User, email=shared_user_email)
        print("Shared user:", shared_user)

        shared_note, created = SharedNotes.objects.get_or_create(
            note=note,
            shared_user=shared_user,
            defaults={"permission": permission, "sharing_date": timezone.now()},
        )

        if not created:
            shared_note.permission = permission
            shared_note.sharing_date = timezone.now()
            shared_note.save()

        return JsonResponse(
            {
                "message": f"Nota compartida con éxito con {shared_user_email} con permiso {permission}."
            },
            status=200,
        )
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return JsonResponse(
            {"error": "Solicitud malformada: JSON inválido."}, status=400
        )
    except Exception as e:
        print("Unexpected error:", str(e))
        return JsonResponse(
            {"error": "Error interno del servidor.", "details": str(e)}, status=500
        )


@login_required
def get_shared_notes(request):
    """
    Retrieve all notes shared with the currently logged-in user.
    """
    try:
        shared_notes = SharedNotes.objects.filter(
            shared_user=request.user
        ).select_related("note")
        shared_notes_list = [
            {
                "note_id": shared_note.note.note_id,
                "title": shared_note.note.title,
                "content": shared_note.note.content,
                "status": shared_note.note.status,
                "shared_by": shared_note.note.creator.email,
                "permission": shared_note.permission,
                "last_modification": shared_note.note.last_modification.isoformat(),
            }
            for shared_note in shared_notes
        ]

        return JsonResponse(
            {"shared_notes": shared_notes_list, "count": len(shared_notes_list)},
            status=200,
        )

    except Exception as e:
        return JsonResponse(
            {"error": "Failed to retrieve shared notes", "details": str(e)}, status=500
        )
