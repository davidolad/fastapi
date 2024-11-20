import time
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# Database connection
while True:
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user='postgres',
            password='password123',
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/posts")
def get_posts():
    try:
        cursor.execute("""SELECT * FROM posts""")
        posts = cursor.fetchall()
        return {"data": posts}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {error}")


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    try:
        cursor.execute(
            """INSERT INTO posts (title, content, published)
               VALUES (%s, %s, %s) RETURNING *""",
            (post.title, post.content, post.published),
        )
        new_post = cursor.fetchone()
        conn.commit()
        return {"data": new_post}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error creating post: {error}")


@app.get("/posts/{id}")
def get_post(id: int):
    try:
        cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
        post = cursor.fetchone()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} was not found",
            )
        return {"data": post}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error fetching post: {error}")


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    try:
        cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
        deleted_post = cursor.fetchone()
        conn.commit()
        if not deleted_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} does not exist",
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error deleting post: {error}")


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    try:
        cursor.execute(
            """UPDATE posts
               SET title = %s, content = %s, published = %s
               WHERE id = %s RETURNING *""",
            (post.title, post.content, post.published, id),
        )
        updated_post = cursor.fetchone()
        conn.commit()
        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} does not exist",
            )
        return {"data": updated_post}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error updating post: {error}")
