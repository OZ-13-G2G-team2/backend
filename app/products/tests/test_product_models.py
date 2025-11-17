import pytest
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_product_create(test_product, test_seller, test_user):
    product = test_product

    # 생성된 데이터 검증
    assert product.product_id is not None
    assert product.name == "삼겹살"
    assert product.seller.user.username == "testuser"

    # ForeignKey 관계 테스트
    assert product.seller == test_seller
    assert product.seller.user == test_user

    # 유효성 검증 테스트
    with pytest.raises(ValidationError):
        product.full_clean()