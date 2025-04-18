from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)

from werkzeug.exceptions import abort, Forbidden

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)
limiter = None


def init_app(app, limiter_instance):
    global limiter
    limiter = limiter_instance


def verify_user_agent():
    user_agent = request.headers.get("User-Agent", "").lower()
    # print(f"user_agent = {user_agent}")
    blocked_user_agents = ["curl", "wget", "python-requests", "httpie"]
    if any(agent in user_agent for agent in blocked_user_agents):
        raise Forbidden("User-Agent interdit.")
        # return JsonResponse({"error": "request from bot"}, status=404)


@bp.route("/")
def index():
    verify_user_agent()

    @limiter.limit("6/minute")
    def limited_index():
        db = get_db()
        posts = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " ORDER BY created DESC"
        ).fetchall()
        return render_template("blog/index.html", posts=posts)

    return limited_index()


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))
    return render_template("blog/create.html")


@bp.route("/post/action", methods=["POST"])
def post_action():
    data = request.get_json()
    post_id = data.get("post_id")

    if not post_id:
        return jsonify({"error": "Post ID manquant"}), 400

    # Exemple d'action : marquer le post comme traité
    db = get_db()
    db.execute("UPDATE post SET title = 'Action' WHERE id = ?", (post_id,))
    db.commit()

    return jsonify({"message": f"Post {post_id} traité avec succès"})


# The blog blueprint has two views. The index view shows all of the posts, most recent first. The create view allows users to create a new post if they are logged in.


def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
