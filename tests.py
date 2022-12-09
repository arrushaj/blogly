from unittest import TestCase

from app import app, db
from models import DEFAULT_IMAGE_URL, User, Post, connect_db
# from models import DEFAULT_IMAGE_URL, User, connect_db

# Let's configure our app to use a different database for tests
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly_test"

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

connect_db(app)

# might need push context here
db.drop_all()
db.create_all()


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.

        Post.query.delete()
        User.query.delete()

        self.client = app.test_client()

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )

        second_user = User(
            first_name="test2_first",
            last_name="test2_last",
            image_url=None,
        )

        db.session.add_all([test_user, second_user])
        db.session.commit() # !must be committed first to create a user to have user id for creating a post

        test_post = Post(
            user_id = test_user.id,
            title="test_title",
            content="test_content"
        )

        db.session.add(test_post)

        db.session.commit()
        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id
        self.post_id = test_post.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_users(self):
        """Tests /users route"""
        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)


    def test_post_new_user(self):
        """Tests adding new user with /users/new"""
        with self.client as c:
            d = {"first_name": "test2_first", "last_name": "test2_last", "image_url": ''}
            resp = c.post("/users/new", data=d, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<h1>test2_first test2_last</h1>", html)
            # self.assertEqual(resp.location, f'/users/{self.user_id}')

    def test_get_new_user(self):
        """Tests getting user information"""
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)


    def test_get_edit_user(self):
        """Tests getting user edit form"""
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}/edit")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<label for="first_name">First Name</label>', html)

    def test_show_post_form(self):
        """Tests showing the form for adding new post."""
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}/posts/new")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Add post for test1_first test1_last', html)

    def test_submit_post_form(self):
        """Tests submitting post form"""
        with self.client as c:
            d = {"title": "blah", "content": "blah"}
            resp = c.post(f"/users/{self.user_id}/posts/new", data=d, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<h1>blah</h1>", html)

    def test_post_detail(self):
        """Tests accessing post details"""
        with self.client as c:
            resp = c.get(f"/posts/{self.post_id}")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<h1>test_title</h1>", html)

    def test_delete_post(self):
        """Tests deleting post"""
        with self.client as c:
            resp = c.post(f"/posts/{self.post_id}/delete", follow_redirects=True)
            print("STUFF", f"/posts/{self.post_id}/delete")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<h1>test1_first test1_last</h1>", html)

""" NOTES: dont tests for assertEqual <html tags>. can be dicey with testing """

