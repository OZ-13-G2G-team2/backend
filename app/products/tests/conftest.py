import pytest
from app.products.models import Product, Seller, Category, CategoryGroup
from app.users.models import User


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email="test@test.com", password="1234", username="testuser"
    )


@pytest.fixture
def test_seller(test_user):
    return Seller.objects.create(
        user=test_user, business_name="테스트 상호", business_number="111-11-11111"
    )


@pytest.fixture
def test_group(db):
    return CategoryGroup.objects.create(name="테스트 그룹")


@pytest.fixture
def test_category(db, test_group):
    return Category.objects.create(name="테스트 카테고리", group=test_group)


@pytest.fixture
def test_product(test_seller, test_category):
    product = Product.objects.create(
        seller=test_seller,
        name="삼겹살",
        origin="한국",
        stock=10,
        price=10000,
        discount_price=6500,
    )
    product.categories.set([test_category])
    return product
