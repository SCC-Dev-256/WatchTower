import pytest
from alembic.config import Config
from alembic import command
from app.database.utils import get_test_db
from app.models.encoder import Encoder, EncoderMetrics, EncoderConfig

def test_migration_upgrade_and_downgrade(test_db):
    """Test that migrations can upgrade and downgrade successfully"""
    alembic_cfg = Config("alembic.ini")
    
    # Test upgrade
    command.upgrade(alembic_cfg, "head")
    
    # Verify models work after upgrade
    encoder = Encoder(
        name="Test Encoder",
        ip_address="192.168.1.100"
    )
    test_db.add(encoder)
    test_db.commit()
    
    # Test downgrade
    command.downgrade(alembic_cfg, "base")

@pytest.mark.parametrize("model", [
    Encoder,
    EncoderMetrics,
    EncoderConfig
])
def test_model_crud_operations(test_db, model):
    """Test CRUD operations for each model"""
    # Create
    instance = model()  # Add required fields based on model
    test_db.add(instance)
    test_db.commit()
    
    # Read
    retrieved = test_db.query(model).first()
    assert retrieved is not None
    
    # Delete
    test_db.delete(retrieved)
    test_db.commit()
    
    assert test_db.query(model).first() is None 