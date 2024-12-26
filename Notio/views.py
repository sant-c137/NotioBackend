from django.http import JsonResponse
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Note, SharedNotes, Tag, NoteTag
import json
from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



User = get_user_model()


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    

@login_required
def google_login_callback(request):
    user = request.user

    social_accounts = SocialAccount.objects.filter(user=user)
    print("Social Account for user:", social_accounts)

    social_account = social_accounts.first()

    if not social_account:
        print("No social account for user:", user)
        return redirect('http://localhost:5173/login/callback/?error=NoSocialAccount')
    
    token = SocialToken.objects.filter(account=social_account, account__provider='google').first()

    if token:
        print('Google token found:', token.token)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return redirect(f'http://localhost:5173/login/callback/?access_token={access_token}')
    else:
        print('No Google token found for user', user)
        return redirect(f'http://localhost:5173/login/callback/?error=NoGoogleToken')


@csrf_exempt
def validate_google_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            google_access_token = data.get('access_token')
            print(google_access_token)

            if not google_access_token:
                return JsonResponse({'detail': 'Access Token is missing.'}, status=400)
            return JsonResponse({'valid': True})
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON.'}, status=400)
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)


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


from django.http import JsonResponse
from social_django.utils import load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth2

@csrf_exempt
def google_login_success(request):
    code = request.GET.get('code', '')
    
    if not code:
        return JsonResponse({'error': 'Code not provided'}, status=400)
    
    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
    
    try:
        user = backend.do_auth(code)
        if user:
            login(request, user)
            return JsonResponse({
                'message': 'Login successful',
                'user': {
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return JsonResponse({'error': 'Authentication failed'}, status=401)
    except Exception as e:
        import traceback
        traceback.print_exc()  
        return JsonResponse({'error': str(e)}, status=500)




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

        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=403)

        user_notes = Note.objects.filter(creator=request.user).order_by(
            "-creation_date"
        )

        if not user_notes.exists():
            return JsonResponse({"notes": [], "count": 0}, status=200)

        notes_list = []
        for note in user_notes:
            try:
                notes_list.append(
                    {
                        "note_id": note.note_id,
                        "title": note.title,
                        "content": note.content,
                        "creation_date": note.creation_date.isoformat(),
                        "last_modification": note.last_modification.isoformat(),
                        "tags": [
                            note_tag.tag.name for note_tag in note.notetag_set.all()
                        ],
                    }
                )
            except AttributeError as attr_error:

                import logging

                logging.error(f"AttributeError in note processing: {attr_error}")
                return JsonResponse(
                    {"error": "Note data is incomplete", "details": str(attr_error)},
                    status=500,
                )

        return JsonResponse({"notes": notes_list, "count": len(notes_list)}, status=200)

    except Note.DoesNotExist as e:

        import logging

        logging.error(f"Note.DoesNotExist error: {e}")
        return JsonResponse({"error": "Notes not found"}, status=404)

    except Exception as e:

        import logging

        logging.error(f"Unexpected error in get_user_notes: {e}")
        return JsonResponse(
            {"error": "Failed to retrieve notes", "details": str(e)}, status=500
        )


@login_required
def create_note(request):
    """
    Create a new note for the currently logged-in user, with optional tags.
    Expects XML input, returns JSON errors.
    """
    if request.method == "POST":
        try:

            import xml.etree.ElementTree as ET

            xml_data = ET.fromstring(request.body)

            title = (
                xml_data.find("title").text
                if xml_data.find("title") is not None
                else None
            )
            content = (
                xml_data.find("content").text
                if xml_data.find("content") is not None
                else None
            )

            tags_elem = xml_data.find("tags")
            tags = (
                [tag.text for tag in tags_elem.findall("tag")]
                if tags_elem is not None
                else []
            )

            if not title or not content:
                return JsonResponse(
                    {"error": "Title and content are required"}, status=400
                )

            new_note = Note.objects.create(
                title=title,
                content=content,
                creation_date=timezone.now(),
                last_modification=timezone.now(),
                creator=request.user,
            )

            if tags:
                tag_objects = []
                for tag_name in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                    tag_objects.append(tag)

                NoteTag.objects.bulk_create(
                    [NoteTag(note=new_note, tag=tag) for tag in tag_objects]
                )

            return JsonResponse(
                {"message": "Note created successfully", "note_id": new_note.note_id},
                status=201,
            )

        except ET.ParseError:

            return JsonResponse({"error": "Invalid XML format"}, status=400)
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
    Edit a note for the currently logged-in user, including updating tags.
    """
    try:
        note = Note.objects.get(note_id=note_id, creator=request.user)
        data = json.loads(request.body)

        note.title = data.get("title", note.title)
        note.content = data.get("content", note.content)
        note.last_modification = timezone.now()

        tags_data = data.get("tags", [])

        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            tags.append(tag)

        note.tags.clear()
        note.tags.add(*tags)

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
                {"error": "note_id, shared_user_email, and permission are required."},
                status=400,
            )

        if permission not in ["view", "edit"]:
            return JsonResponse({"error": "Invalid permission type."}, status=400)

        try:
            shared_user = User.objects.get(email=shared_user_email)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": f"User with email {shared_user_email} does not exist."},
                status=404,
            )

        note = get_object_or_404(Note, pk=note_id, creator=request.user)
        print("Note retrieved:", note)

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
                "message": f"Note successfully shared with {shared_user_email} with {permission} permission."
            },
            status=200,
        )
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return JsonResponse({"error": "Malformed request: invalid JSON."}, status=400)
    except Exception as e:
        print("Unexpected error:", str(e))
        return JsonResponse(
            {"error": "Internal server error.", "details": str(e)}, status=500
        )


@login_required
def get_shared_notes(request):
    """
    Retrieve all notes shared with the currently logged-in user, including tags.
    """
    try:
        shared_notes = (
            SharedNotes.objects.filter(shared_user=request.user)
            .select_related("note")
            .prefetch_related("note__tags")
        )

        shared_notes_list = [
            {
                "shared_note_id": shared_note.note.note_id,
                "title": shared_note.note.title,
                "content": shared_note.note.content,
                "tags": [tag.name for tag in shared_note.note.tags.all()],
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


@login_required
def edit_shared_note(request, note_id):
    """
    Edit a shared note if the currently logged-in user has the 'edit' permission.
    """
    try:

        shared_note = SharedNotes.objects.get(
            note__note_id=note_id, shared_user=request.user
        )

        if shared_note.permission != "edit":
            return JsonResponse(
                {"error": "You do not have permission to edit this note."}, status=403
            )

        note = shared_note.note

        data = json.loads(request.body)

        note.title = data.get("title", note.title)
        note.content = data.get("content", note.content)
        note.last_modification = timezone.now()

        tags_data = data.get("tags", [])
        if tags_data is not None:
            tags = []
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                tags.append(tag)

            note.tags.clear()
            note.tags.add(*tags)

        note.save()

        return JsonResponse({"message": "Shared note updated successfully"}, status=200)

    except SharedNotes.DoesNotExist:
        return JsonResponse({"error": "Shared note not found"}, status=404)
    except Note.DoesNotExist:
        return JsonResponse(
            {"error": "Note associated with shared note not found"}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"error": "Failed to update shared note", "details": str(e)}, status=500
        )
