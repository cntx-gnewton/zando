"""
Database seeding script.

This script initializes the database with reference data needed for the Zando application.
It reads data from CSV files in the seed_data/csv directory and inserts it into the database.
"""

import logging
import argparse
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.db import get_db_engine, get_db_session
from database.models import (
    SNP, SNPCharacteristicLink, SNPIngredientLink, SNPIngredientCautionLink,
    SkinCharacteristic, SkinCondition, CharacteristicConditionLink, ConditionIngredientLink,
    Ingredient, IngredientCaution
)
from database.seed_data.seed_utils import load_csv_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def seed_snps(session):
    """
    Seed the SNP table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(SNP).count()
    if existing_count > 0:
        logger.info(f"SNP table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    snps_data = load_csv_data('snps.csv')
    if not snps_data:
        logger.warning("No SNP data found in CSV. Skipping SNP seeding.")
        return
        
    # Add SNP records
    for snp_data in snps_data:
        snp = SNP(**snp_data)
        session.add(snp)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(snps_data)} SNP records to the database")

def seed_characteristics(session):
    """
    Seed the SkinCharacteristic table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(SkinCharacteristic).count()
    if existing_count > 0:
        logger.info(f"SkinCharacteristic table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    characteristics_data = load_csv_data('skin_characteristics.csv')
    if not characteristics_data:
        logger.warning("No characteristic data found in CSV. Skipping SkinCharacteristic seeding.")
        return
        
    # Add SkinCharacteristic records
    for char_data in characteristics_data:
        characteristic = SkinCharacteristic(**char_data)
        session.add(characteristic)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(characteristics_data)} SkinCharacteristic records to the database")

def seed_conditions(session):
    """
    Seed the SkinCondition table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(SkinCondition).count()
    if existing_count > 0:
        logger.info(f"SkinCondition table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    conditions_data = load_csv_data('skin_conditions.csv')
    if not conditions_data:
        logger.warning("No condition data found in CSV. Skipping SkinCondition seeding.")
        return
        
    # Add SkinCondition records
    for cond_data in conditions_data:
        condition = SkinCondition(**cond_data)
        session.add(condition)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(conditions_data)} SkinCondition records to the database")

def seed_ingredients(session):
    """
    Seed the Ingredient table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(Ingredient).count()
    if existing_count > 0:
        logger.info(f"Ingredient table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    ingredients_data = load_csv_data('ingredients.csv')
    if not ingredients_data:
        logger.warning("No ingredient data found in CSV. Skipping Ingredient seeding.")
        return
        
    # Add Ingredient records
    for ing_data in ingredients_data:
        ingredient = Ingredient(**ing_data)
        session.add(ingredient)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(ingredients_data)} Ingredient records to the database")

def seed_ingredient_cautions(session):
    """
    Seed the IngredientCaution table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(IngredientCaution).count()
    if existing_count > 0:
        logger.info(f"IngredientCaution table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    caution_data = load_csv_data('ingredient_cautions.csv')
    if not caution_data:
        logger.warning("No ingredient caution data found in CSV. Skipping IngredientCaution seeding.")
        return
        
    # Add IngredientCaution records
    for caution in caution_data:
        ingredient_caution = IngredientCaution(**caution)
        session.add(ingredient_caution)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(caution_data)} IngredientCaution records to the database")

def seed_snp_characteristic_links(session):
    """
    Seed the SNP-Characteristic association table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(SNPCharacteristicLink).count()
    if existing_count > 0:
        logger.info(f"SNPCharacteristicLink table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    links_data = load_csv_data('snp_characteristic_links.csv')
    if not links_data:
        logger.warning("No SNP-Characteristic link data found in CSV. Skipping SNPCharacteristicLink seeding.")
        return
        
    # We need to find the appropriate IDs
    for link_data in links_data:
        snp_rsid = link_data['snp_rsid']
        char_name = link_data['characteristic_name']
        
        # Find the SNP ID
        snp = session.query(SNP).filter(SNP.rsid == snp_rsid).first()
        if not snp:
            logger.warning(f"SNP with rsid {snp_rsid} not found. Skipping link.")
            continue
            
        # Find the Characteristic ID
        characteristic = session.query(SkinCharacteristic).filter(SkinCharacteristic.name == char_name).first()
        if not characteristic:
            logger.warning(f"SkinCharacteristic with name {char_name} not found. Skipping link.")
            continue
            
        # Create and add the link
        link = SNPCharacteristicLink(
            snp_id=snp.snp_id,
            characteristic_id=characteristic.characteristic_id,
            effect_direction=link_data['effect_direction'],
            evidence_strength=link_data['evidence_strength']
        )
        session.add(link)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(links_data)} SNP-Characteristic links to the database")

def seed_characteristic_condition_links(session):
    """
    Seed the Characteristic-Condition association table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(CharacteristicConditionLink).count()
    if existing_count > 0:
        logger.info(f"CharacteristicConditionLink table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    links_data = load_csv_data('characteristic_condition_links.csv')
    if not links_data:
        logger.warning("No Characteristic-Condition link data found in CSV. Skipping CharacteristicConditionLink seeding.")
        return
        
    # We need to find the appropriate IDs
    for link_data in links_data:
        char_name = link_data['characteristic_name']
        cond_name = link_data['condition_name']
        
        # Find the Characteristic ID
        characteristic = session.query(SkinCharacteristic).filter(SkinCharacteristic.name == char_name).first()
        if not characteristic:
            logger.warning(f"SkinCharacteristic with name {char_name} not found. Skipping link.")
            continue
            
        # Find the Condition ID
        condition = session.query(SkinCondition).filter(SkinCondition.name == cond_name).first()
        if not condition:
            logger.warning(f"SkinCondition with name {cond_name} not found. Skipping link.")
            continue
            
        # Create and add the link
        link = CharacteristicConditionLink(
            characteristic_id=characteristic.characteristic_id,
            condition_id=condition.condition_id,
            relationship_type=link_data['relationship_type']
        )
        session.add(link)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(links_data)} Characteristic-Condition links to the database")

def seed_condition_ingredient_links(session):
    """
    Seed the Condition-Ingredient association table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(ConditionIngredientLink).count()
    if existing_count > 0:
        logger.info(f"ConditionIngredientLink table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    links_data = load_csv_data('condition_ingredient_links.csv')
    if not links_data:
        logger.warning("No Condition-Ingredient link data found in CSV. Skipping ConditionIngredientLink seeding.")
        return
        
    # We need to find the appropriate IDs
    for link_data in links_data:
        cond_name = link_data['condition_name']
        ing_name = link_data['ingredient_name']
        
        # Find the Condition ID
        condition = session.query(SkinCondition).filter(SkinCondition.name == cond_name).first()
        if not condition:
            logger.warning(f"SkinCondition with name {cond_name} not found. Skipping link.")
            continue
            
        # Find the Ingredient ID
        ingredient = session.query(Ingredient).filter(Ingredient.name == ing_name).first()
        if not ingredient:
            logger.warning(f"Ingredient with name {ing_name} not found. Skipping link.")
            continue
            
        # Create and add the link
        link = ConditionIngredientLink(
            condition_id=condition.condition_id,
            ingredient_id=ingredient.ingredient_id,
            recommendation_strength=link_data['recommendation_strength'],
            guidance_notes=link_data['guidance_notes']
        )
        session.add(link)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(links_data)} Condition-Ingredient links to the database")

def seed_snp_ingredient_links(session):
    """
    Seed the SNP-Ingredient association table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(SNPIngredientLink).count()
    if existing_count > 0:
        logger.info(f"SNPIngredientLink table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    links_data = load_csv_data('snp_ingredient_links.csv')
    if not links_data:
        logger.warning("No SNP-Ingredient link data found in CSV. Skipping SNPIngredientLink seeding.")
        return
        
    # We need to find the appropriate IDs
    for link_data in links_data:
        snp_rsid = link_data['snp_rsid']
        ing_name = link_data['ingredient_name']
        
        # Find the SNP ID
        snp = session.query(SNP).filter(SNP.rsid == snp_rsid).first()
        if not snp:
            logger.warning(f"SNP with rsid {snp_rsid} not found. Skipping link.")
            continue
            
        # Find the Ingredient ID
        ingredient = session.query(Ingredient).filter(Ingredient.name == ing_name).first()
        if not ingredient:
            logger.warning(f"Ingredient with name {ing_name} not found. Skipping link.")
            continue
            
        # Create and add the link
        link = SNPIngredientLink(
            snp_id=snp.snp_id,
            ingredient_id=ingredient.ingredient_id,
            benefit_mechanism=link_data['benefit_mechanism'],
            recommendation_strength=link_data['recommendation_strength'],
            evidence_level=link_data['evidence_level']
        )
        session.add(link)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(links_data)} SNP-Ingredient links to the database")

def seed_snp_ingredient_caution_links(session):
    """
    Seed the SNP-IngredientCaution association table with reference data from CSV.
    
    Args:
        session: SQLAlchemy session
    """
    # First check if table already has data
    existing_count = session.query(SNPIngredientCautionLink).count()
    if existing_count > 0:
        logger.info(f"SNPIngredientCautionLink table already contains {existing_count} records. Skipping seeding.")
        return
        
    # Load data from CSV
    links_data = load_csv_data('snp_ingredient_caution_links.csv')
    if not links_data:
        logger.warning("No SNP-IngredientCaution link data found in CSV. Skipping SNPIngredientCautionLink seeding.")
        return
        
    # We need to find the appropriate IDs
    for link_data in links_data:
        snp_rsid = link_data['snp_rsid']
        caution_name = link_data['ingredient_name']
        
        # Find the SNP ID
        snp = session.query(SNP).filter(SNP.rsid == snp_rsid).first()
        if not snp:
            logger.warning(f"SNP with rsid {snp_rsid} not found. Skipping link.")
            continue
            
        # Find the IngredientCaution ID
        caution = session.query(IngredientCaution).filter(IngredientCaution.ingredient_name == caution_name).first()
        if not caution:
            logger.warning(f"IngredientCaution with name {caution_name} not found. Skipping link.")
            continue
            
        # Create and add the link
        link = SNPIngredientCautionLink(
            snp_id=snp.snp_id,
            caution_id=caution.caution_id,
            evidence_level=link_data['evidence_level'],
            notes=link_data['notes']
        )
        session.add(link)
    
    # Commit the changes
    session.commit()
    logger.info(f"Added {len(links_data)} SNP-IngredientCaution links to the database")

def seed_all():
    """
    Seed all reference data tables.
    
    This is the main entry point for database seeding.
    """
    with get_db_session() as session:
        logger.info("Starting database seeding from CSV files")
        
        # Seed core tables first
        seed_snps(session)
        seed_characteristics(session)
        seed_conditions(session)
        seed_ingredients(session)
        seed_ingredient_cautions(session)
        
        # Then seed association tables
        seed_snp_characteristic_links(session)
        seed_characteristic_condition_links(session)  
        seed_condition_ingredient_links(session)
        seed_snp_ingredient_links(session)
        seed_snp_ingredient_caution_links(session)
        
        logger.info("Database seeding completed successfully")

def truncate_all():
    """
    Truncate all tables to start with a clean database.
    
    WARNING: This will delete all data in the tables.
    """
    engine = get_db_engine()
    
    with engine.begin() as conn:
        logger.info("Truncating all tables")
        
        # Truncate tables in reverse order of dependencies
        conn.execute(text("TRUNCATE TABLE snp_ingredientcaution_link CASCADE"))
        conn.execute(text("TRUNCATE TABLE snp_ingredient_link CASCADE"))
        conn.execute(text("TRUNCATE TABLE condition_ingredient_link CASCADE"))
        conn.execute(text("TRUNCATE TABLE characteristic_condition_link CASCADE"))
        conn.execute(text("TRUNCATE TABLE snp_characteristic_link CASCADE"))
        conn.execute(text("TRUNCATE TABLE ingredient CASCADE"))
        conn.execute(text("TRUNCATE TABLE ingredientcaution CASCADE"))
        conn.execute(text("TRUNCATE TABLE skincondition CASCADE"))
        conn.execute(text("TRUNCATE TABLE skincharacteristic CASCADE"))
        conn.execute(text("TRUNCATE TABLE snp CASCADE"))
        
        logger.info("All tables truncated successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the database with reference data")
    parser.add_argument("--truncate", action="store_true", help="Truncate all tables before seeding")
    
    args = parser.parse_args()
    
    if args.truncate:
        truncate_all()
    
    seed_all()