"""
Create evaluation datasets for AWS Bedrock Knowledge Base evaluation.
Generates JSONL files in AWS Bedrock conversationTurns format.
"""

import json
from pathlib import Path
from typing import List, Dict
from loguru import logger

# F1 evaluation questions covering different regulation categories
EVALUATION_QUESTIONS = [
    # Points System
    {
        "prompt": "How many points does the driver finishing in 1st place receive?",
        "referenceResponse": "The driver finishing in 1st place receives 25 championship points in a standard Formula 1 race.",
        "category": "points_system"
    },
    {
        "prompt": "What are the points awarded for positions 1st through 10th?",
        "referenceResponse": "Points are awarded as follows: 1st place - 25 points, 2nd - 18, 3rd - 15, 4th - 12, 5th - 10, 6th - 8, 7th - 6, 8th - 4, 9th - 2, 10th - 1 point.",
        "category": "points_system"
    },
    {
        "prompt": "Does the fastest lap earn any points?",
        "referenceResponse": "The fastest lap in a Formula 1 race does not earn any points. The points are awarded based on the final race classification.",
        "category": "points_system"
    },
    # Power Unit
    {
        "prompt": "What are the main components of an F1 power unit?",
        "referenceResponse": "An F1 power unit consists of: 1) Internal Combustion Engine (ICE) - 1.6L V6 turbo, 2) MGU-K (Motor Generator Unit - Kinetic), 3) MGU-H (Motor Generator Unit - Heat), 4) Turbocharger, 5) Energy Store (battery), 6) Control Electronics.",
        "category": "technical_regulations"
    },
    
    # Parc Fermé
    {
        "prompt": "What is parc fermé and when does it apply?",
        "referenceResponse": "Parc fermé is a period where cars are in a restricted area and limited work can be performed. It begins when cars exit the pit lane for qualifying and continues until the start of the race. During this time, only specific permitted work is allowed.",
        "category": "sporting_regulations"
    },
    {
        "prompt": "Can teams make setup changes after qualifying?",
        "referenceResponse": "No, after qualifying, cars enter parc fermé conditions where setup changes are prohibited. Only specific repairs and adjustments (like front wing angle) are permitted. Any significant changes require starting from the pit lane.",
        "category": "sporting_regulations"
    },
    
    # Pit Stop Rules
    {
        "prompt": "What is the minimum time for a pit stop?",
        "referenceResponse": "There is no minimum pit stop time mandated by regulations. However, practical pit stops typically take 2-3 seconds for a tyre change. Teams must ensure safe releases without endangering other competitors or personnel.",
        "category": "sporting_regulations"
    },
    {
        "prompt": "How many mechanics can work on a car during a pit stop?",
        "referenceResponse": "The regulations do not specify a limit on the number of mechanics that can work on a Formula 1 car during a pit stop.",
        "category": "sporting_regulations"
    },
    
    # Pit Lane Rules
    {
        "prompt": "What is the pit lane speed limit during the whole Competition unless changed by the Race Director?",
        "referenceResponse": "The pit lane speed limit during the whole Competition is typically 80 km/h, unless changed by the Race Director.",
        "category": "sporting_regulations"
    },

    # Practice Sessions
    {
        "prompt": "How many free practice sessions are held when a sprint session is not scheduled?",
        "referenceResponse": "When a sprint session is not scheduled, there are typically three free practice sessions held during a race weekend.",
        "category": "sporting_regulations"
    },

    # Championship Rules
    {
        "prompt": "How many drivers may each Competitor use in races during a Championship?",
        "referenceResponse": "Each Formula 1 team can enter two cars in the championship. The drivers for those two cars must be named in the team's application to compete in the championship.",
        "category": "sporting_regulations"
    },

    # Body Work
    {
        "prompt": "Which components are not considered to be bodywork?",
        "referenceResponse": "Cameras and housings, rear view mirrors, the ERS status light, mechanical parts of the power train or steering system, wheel rims and tyres, and brake disc assemblies, calipers, and pads.",
        "category": "sporting_regulations"
    },
]


def create_bedrock_format_dataset(
    output_path: Path,
    questions: List[Dict],
    include_reference_responses: bool = True
) -> None:
    """
    Create evaluation dataset in AWS Bedrock's conversationTurns JSONL format.
    
    Format per AWS documentation:
    {
        "conversationTurns": [
            {
                "prompt": {
                    "content": [{"text": "prompt text"}]
                },
                "referenceResponses": [
                    {
                        "content": [{"text": "reference response"}]
                    }
                ]
            }
        ]
    }
    
    Args:
        output_path: Path to save the JSONL file
        questions: List of evaluation questions with reference responses
        include_reference_responses: Whether to include reference responses
    """
    logger.info(f"Creating AWS Bedrock evaluation dataset: {output_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, item in enumerate(questions, 1):
            # Build conversation turn structure
            conversation_turn = {
                "prompt": {
                    "content": [
                        {"text": item["prompt"]}
                    ]
                }
            }
            
            # Add reference response if requested
            if include_reference_responses and "referenceResponse" in item:
                conversation_turn["referenceResponses"] = [
                    {
                        "content": [
                            {"text": item["referenceResponse"]}
                        ]
                    }
                ]
            
            # Wrap in conversationTurns array (single turn per record)
            record = {
                "conversationTurns": [conversation_turn]
            }
            
            # Write as JSON line
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            logger.debug(
                f"Added question {idx}/{len(questions)}: "
                f"{item['prompt'][:50]}..."
            )
    
    logger.success(
        f"✅ Created dataset with {len(questions)} questions: {output_path}"
    )
    logger.info(f"   Format: AWS Bedrock conversationTurns structure")
    logger.info(
        f"   Reference responses: "
        f"{'Included' if include_reference_responses else 'Not included'}"
    )


def validate_dataset(file_path: Path) -> bool:
    """
    Validate dataset format matches AWS Bedrock requirements.
    
    Args:
        file_path: Path to JSONL dataset file
    
    Returns:
        True if valid, False otherwise
    """
    logger.info(f"Validating dataset: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_num = 0
            for line in f:
                line_num += 1
                
                # Parse JSON
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Line {line_num}: Invalid JSON - {e}")
                    return False
                
                # Check required structure
                if "conversationTurns" not in record:
                    logger.error(
                        f"❌ Line {line_num}: Missing 'conversationTurns' key"
                    )
                    return False
                
                if not isinstance(record["conversationTurns"], list):
                    logger.error(
                        f"❌ Line {line_num}: 'conversationTurns' must be array"
                    )
                    return False
                
                if len(record["conversationTurns"]) == 0:
                    logger.error(
                        f"❌ Line {line_num}: 'conversationTurns' is empty"
                    )
                    return False
                
                if len(record["conversationTurns"]) > 5:
                    logger.error(
                        f"❌ Line {line_num}: Too many turns "
                        f"({len(record['conversationTurns'])} > 5 max)"
                    )
                    return False
                
                # Validate each turn
                for turn_idx, turn in enumerate(record["conversationTurns"]):
                    if "prompt" not in turn:
                        logger.error(
                            f"❌ Line {line_num}, Turn {turn_idx+1}: "
                            f"Missing 'prompt' key"
                        )
                        return False
                    
                    if "content" not in turn["prompt"]:
                        logger.error(
                            f"❌ Line {line_num}, Turn {turn_idx+1}: "
                            f"Missing 'prompt.content'"
                        )
                        return False
                    
                    if not isinstance(turn["prompt"]["content"], list):
                        logger.error(
                            f"❌ Line {line_num}, Turn {turn_idx+1}: "
                            f"'prompt.content' must be array"
                        )
                        return False
                    
                    if len(turn["prompt"]["content"]) == 0:
                        logger.error(
                            f"❌ Line {line_num}, Turn {turn_idx+1}: "
                            f"'prompt.content' is empty"
                        )
                        return False
                    
                    if "text" not in turn["prompt"]["content"][0]:
                        logger.error(
                            f"❌ Line {line_num}, Turn {turn_idx+1}: "
                            f"Missing 'prompt.content[0].text'"
                        )
                        return False
                    
                    # Validate referenceResponses if present
                    if "referenceResponses" in turn:
                        if not isinstance(turn["referenceResponses"], list):
                            logger.error(
                                f"❌ Line {line_num}, Turn {turn_idx+1}: "
                                f"'referenceResponses' must be array"
                            )
                            return False
                        
                        if len(turn["referenceResponses"]) > 0:
                            ref_resp = turn["referenceResponses"][0]
                            if "content" not in ref_resp:
                                logger.error(
                                    f"❌ Line {line_num}, Turn {turn_idx+1}: "
                                    f"Missing 'referenceResponses[0].content'"
                                )
                                return False
                            
                            if not isinstance(ref_resp["content"], list):
                                logger.error(
                                    f"❌ Line {line_num}, Turn {turn_idx+1}: "
                                    f"'referenceResponses[0].content' must be array"
                                )
                                return False
                            
                            if (len(ref_resp["content"]) > 0 and 
                                "text" not in ref_resp["content"][0]):
                                logger.error(
                                    f"❌ Line {line_num}, Turn {turn_idx+1}: "
                                    f"Missing 'referenceResponses[0].content[0].text'"
                                )
                                return False
        
        logger.success(f"✅ Dataset is valid! ({line_num} records)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        return False


def main():
    """Create evaluation datasets in AWS Bedrock format."""
    logger.info("="*70)
    logger.info("Creating AWS Bedrock Evaluation Datasets")
    logger.info("="*70)
    
    # Output directory
    output_dir = Path("evaluation_datasets")
    
    # 1. Full dataset with reference responses (MAIN DATASET)
    main_dataset = output_dir / "f1-kb-evaluation-bedrock.jsonl"
    create_bedrock_format_dataset(
        output_path=main_dataset,
        questions=EVALUATION_QUESTIONS,
        include_reference_responses=True
    )
    
    # 2. Prompts-only dataset (no reference responses)
    prompts_only = output_dir / "f1-kb-evaluation-prompts-only.jsonl"
    create_bedrock_format_dataset(
        output_path=prompts_only,
        questions=EVALUATION_QUESTIONS,
        include_reference_responses=False
    )
    
    # 3. Validate datasets
    logger.info("\n" + "="*70)
    logger.info("Validating Datasets")
    logger.info("="*70)
    
    main_valid = validate_dataset(main_dataset)
    prompts_valid = validate_dataset(prompts_only)
    
    # 4. Summary
    logger.info("\n" + "="*70)
    logger.success("Evaluation Dataset Creation Complete!")
    logger.info("="*70)
    logger.info(f"\n📊 Generated Files:")
    logger.info(f"   1. {main_dataset}")
    logger.info(f"      ├─ Questions: {len(EVALUATION_QUESTIONS)}")
    logger.info(f"      ├─ Reference responses: ✅ Included")
    logger.info(
        f"      └─ Validation: {'✅ PASSED' if main_valid else '❌ FAILED'}"
    )
    logger.info(f"\n   2. {prompts_only}")
    logger.info(f"      ├─ Questions: {len(EVALUATION_QUESTIONS)}")
    logger.info(f"      ├─ Reference responses: ❌ Not included")
    logger.info(
        f"      └─ Validation: {'✅ PASSED' if prompts_valid else '❌ FAILED'}"
    )
    
    logger.info("\n" + "="*70)
    logger.info("Next Steps:")
    logger.info("="*70)
    logger.info("\n1️⃣  Upload to S3:")
    logger.info(
        f"   aws s3 cp {output_dir}/ "
        f"s3://YOUR-BUCKET-NAME/evaluations/ --recursive"
    )
    
    logger.info("\n2️⃣  Create Evaluation Job in AWS Console:")
    logger.info(
        "   • Navigate to: Bedrock → Knowledge Bases → Your KB → Evaluations"
    )
    logger.info("   • Click: 'Create evaluation job'")
    logger.info(
        "   • Dataset S3 URI: "
        "s3://YOUR-BUCKET-NAME/evaluations/f1-kb-evaluation-bedrock.jsonl"
    )
    logger.info("   • Evaluation type: Retrieve and generate")
    logger.info(
        "   • Model: anthropic.claude-3-haiku-20240307-v1:0"
    )
    
    logger.info("\n3️⃣  Wait for Results (10-30 minutes)")
    
    logger.info("\n" + "="*70)


if __name__ == "__main__":
    from src.utils.logger import setup_logger
    setup_logger()
    main()