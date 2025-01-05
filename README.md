# Quality Wheel - AI Practice Validation System

The Quality Wheel is a sophisticated validation system designed to evaluate AI practices across multiple dimensions using a configurable set of criteria and thresholds.

## Overview

The Quality Wheel evaluates practices using six main criteria:

1. **Quality (Q)**
   - Fullness (40%) *required*
   - Structure (30%) *required*
   - Examples (15%)
   - Limitations (15%)

2. **Reproducibility (R)**
   - Steps Clarity (40%) *required*
   - Requirements (30%) *required*
   - Resources (30%) *required*

3. **Utility (U)**
   - Problem Clarity (35%) *required*
   - Benefits (35%) *required*
   - Efficiency (30%)

4. **Applicability (A)**
   - Universality (35%) *required*
   - Scalability (35%) *required*
   - Constraints (30%)

5. **Innovation (I)**
   - Novelty (40%)
   - Technical Complexity (30%)
   - Potential (30%) *required*

6. **Reliability (Rel)**
   - Empirical Validation (35%) *required*
   - Methodology (25%) *required*
   - Adaptability (20%)
   - External Validation (20%)

## Validation Process

1. Each criterion is evaluated based on its sub-criteria
2. Each sub-criterion has:
   - Minimum threshold value (default: 6.0)
   - Weight coefficient
   - Required flag

3. The validation process includes:
   - Individual scoring of each sub-criterion
   - Weighted aggregation of scores
   - Validation against minimum thresholds
   - Generation of recommendations for improvement

## Scoring System

- Scores range from 0 to 10
- Required criteria must meet minimum threshold (default: 6.0)
- Final score is calculated as weighted average of valid scores
- Practice is marked for review if any required criterion fails

## Usage

### Basic Usage
```python
from validator_service.quality_wheel import QualityWheel

wheel = QualityWheel()
validation_result = wheel.evaluate_practice(practice_data)
```

### Adjusting Thresholds
```python
# Adjust minimum threshold for quality fullness
wheel.adjust_threshold(
    criterion="Q",
    metric="fullness",
    min_value=7.0,
    weight=0.5,
    required=True
)
```

### Validation Result Structure
```python
{
    "valid_scores": {
        "criterion": {
            "score": float,
            "details": dict,
            "explanation": str,
            "is_valid": bool
        }
    },
    "invalid_scores": {...},
    "missing_required": [],
    "final_score": float,
    "recommendations": []
}
```

## Decision Making

The system makes decisions based on the following rules:
- **Approve**: Final score ≥ 7.0
- **Review**: 5.0 ≤ Final score < 7.0
- **Reject**: Final score < 5.0
- **Needs Improvement**: Missing required criteria

## Recommendations

The system provides recommendations when:
- Any criterion scores below threshold
- Required criteria are missing
- Improvements could enhance overall quality

## Configuration

The Quality Wheel is highly configurable:
- Threshold values can be adjusted per criterion
- Weights can be modified
- Required flags can be toggled
- New criteria can be added through the configuration

## Integration

The Quality Wheel can be integrated with:
- Practice validation pipelines
- Quality assurance systems
- Automated review processes
- Continuous improvement workflows

## Error Handling

The system includes robust error handling for:
- Invalid input data
- Missing required fields
- Calculation errors
- Configuration issues

## Future Improvements

Planned enhancements include:
- Dynamic threshold adjustment based on practice domain
- Machine learning-based scoring optimization
- Extended recommendation system
- Integration with external validation sources

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any enhancements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 