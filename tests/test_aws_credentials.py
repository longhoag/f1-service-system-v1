"""Test AWS credentials are configured correctly"""
import sys
import os
import boto3
from loguru import logger

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings
from src.utils.logger import setup_logger

def test_aws_credentials():
    """Verify AWS credentials can access Bedrock and Knowledge Base"""
    
    # Setup logger
    setup_logger()
    
    logger.info("Testing AWS credentials and Bedrock access...")
    logger.info(f"Region: {settings.aws_region}")
    
    try:
        # Test 1: STS (Security Token Service) - verifies credentials work
        logger.info("\n[1/4] Testing AWS credential validity...")
        sts = boto3.client(
            'sts',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        
        identity = sts.get_caller_identity()
        logger.success(f"✅ AWS credentials valid")
        logger.info(f"Account: {identity['Account']}")
        logger.info(f"User ARN: {identity['Arn']}")
        
        # Test 2: Bedrock model access
        logger.info("\n[2/4] Testing Bedrock service access...")
        bedrock = boto3.client(
            'bedrock',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        
        models = bedrock.list_foundation_models()
        model_count = len(models.get('modelSummaries', []))
        logger.success(f"✅ Bedrock access confirmed ({model_count} models available)")
        
        # Check specific models
        titan_found = False
        claude_found = False
        
        for model in models.get('modelSummaries', []):
            model_id = model.get('modelId', '')
            if 'titan-embed-text-v2' in model_id:
                titan_found = True
                logger.info(f"  ✓ Found embedding model: {model_id}")
            if 'claude-3-5-sonnet' in model_id:
                claude_found = True
                logger.info(f"  ✓ Found generation model: {model_id}")
        
        if not titan_found:
            logger.warning(f"⚠️ Titan Embeddings V2 not found. Check model access.")
        if not claude_found:
            logger.warning(f"⚠️ Claude 3.5 Sonnet not found. Check model access.")
        
        # Test 3: Knowledge Base access
        logger.info("\n[3/4] Testing Knowledge Base access...")
        bedrock_agent = boto3.client(
            'bedrock-agent',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        
        kb_list = bedrock_agent.list_knowledge_bases(maxResults=10)
        kb_count = len(kb_list.get('knowledgeBaseSummaries', []))
        logger.success(f"✅ Knowledge Base access confirmed ({kb_count} KBs found)")
        
        # Test 4: Specific Knowledge Base retrieval
        if settings.bedrock_kb_id:
            logger.info(f"\n[4/4] Testing specific KB: {settings.bedrock_kb_id}")
            
            kb_details = bedrock_agent.get_knowledge_base(
                knowledgeBaseId=settings.bedrock_kb_id
            )
            
            kb = kb_details['knowledgeBase']
            logger.success(f"✅ Knowledge Base accessible")
            logger.info(f"Name: {kb.get('name', 'N/A')}")
            logger.info(f"Status: {kb.get('status', 'Unknown')}")
            logger.info(f"Created: {kb.get('createdAt', 'Unknown')}")
            
            # Check data sources
            ds_response = bedrock_agent.list_data_sources(
                knowledgeBaseId=settings.bedrock_kb_id
            )
            
            data_sources = ds_response.get('dataSourceSummaries', [])
            logger.info(f"Data Sources: {len(data_sources)}")
            
            for ds in data_sources:
                logger.info(f"  • {ds.get('name', 'Unknown')}: {ds.get('status', 'Unknown')}")
        else:
            logger.warning("⚠️ BEDROCK_KNOWLEDGE_BASE_ID not set - skipping KB test")
        
        logger.success("\n🎉 All AWS credential tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ AWS credential test failed: {e}")
        logger.error("\nTroubleshooting steps:")
        logger.error("1. Check .env has correct AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        logger.error("2. Verify IAM user has AmazonBedrockFullAccess policy")
        logger.error("3. Confirm model access in Bedrock console")
        return False

if __name__ == "__main__":
    test_aws_credentials()
