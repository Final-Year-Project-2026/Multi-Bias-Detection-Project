"""
Multi-Bias Detection System with Context-Aware Analysis
Supports: Gender, Age, Socioeconomic, Regional/Geographic, and Sentiment Bias

This implementation uses CONTEXTUAL ANALYSIS instead of simple keyword counting:
- Analyzes associations between entities and descriptors
- Detects stereotypical patterns in language
- Considers semantic relationships, not just word frequency
- Weights profession-gender associations more heavily than simple counts
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple

class BiasDetector:
    """Base class for all bias detection"""
    
    def __init__(self, bias_type: str):
        self.bias_type = bias_type
        
    def detect(self, text: str) -> Dict:
        """Detect bias in text - to be implemented by subclasses"""
        raise NotImplementedError
        
    def get_bias_label(self, score: float) -> str:
        """Convert bias score to human-readable label"""
        if abs(score) > 0.5:
            return "STRONG BIAS"
        elif abs(score) > 0.3:
            return "MODERATE BIAS"
        elif abs(score) > 0.1:
            return "SLIGHT BIAS"
        else:
            return "NEUTRAL"


class GenderBiasDetector(BiasDetector):
    """Detect gender bias using contextual profession-gender association analysis"""
    
    MALE_PRONOUNS = ['he', 'him', 'his', 'himself']
    FEMALE_PRONOUNS = ['she', 'her', 'hers', 'herself']
    
    # Professions/roles to analyze for gender associations
    PROFESSIONS = [
        'doctor', 'nurse', 'engineer', 'teacher', 'ceo', 'secretary',
        'pilot', 'flight attendant', 'programmer', 'developer', 'scientist',
        'assistant', 'manager', 'worker', 'employee', 'professional',
        'lawyer', 'judge', 'officer', 'firefighter', 'chef', 'cook',
        'mechanic', 'accountant', 'receptionist', 'designer', 'artist'
    ]
    
    def __init__(self):
        super().__init__('gender')
        
    def detect(self, text: str) -> Dict:
        """Detect gender bias through contextual analysis"""
        text_lower = text.lower()
        sentences = re.split(r'[.!?]+', text)
        
        # Count basic pronouns
        male_count = sum(len(re.findall(r'\b' + p + r'\b', text_lower)) 
                        for p in self.MALE_PRONOUNS)
        female_count = sum(len(re.findall(r'\b' + p + r'\b', text_lower)) 
                          for p in self.FEMALE_PRONOUNS)
        
        # Analyze profession-gender associations (KEY IMPROVEMENT)
        associations = []
        for sentence in sentences:
            sentence = sentence.lower().strip()
            if not sentence:
                continue
                
            # Check if sentence contains a profession
            for profession in self.PROFESSIONS:
                if profession in sentence:
                    # Check which gender pronoun appears near this profession
                    has_male = any(re.search(r'\b' + p + r'\b', sentence) for p in self.MALE_PRONOUNS)
                    has_female = any(re.search(r'\b' + p + r'\b', sentence) for p in self.FEMALE_PRONOUNS)
                    
                    if has_male and not has_female:
                        associations.append({'profession': profession, 'gender': 'male', 'sentence': sentence[:100]})
                        male_count += 2  # Weight associations more heavily
                    elif has_female and not has_male:
                        associations.append({'profession': profession, 'gender': 'female', 'sentence': sentence[:100]})
                        female_count += 2  # Weight associations more heavily
        
        # Calculate contextual bias score
        total = male_count + female_count
        bias_score = (male_count - female_count) / total if total > 0 else 0.0
        
        # Analyze stereotypical patterns
        stereotype_score = self._detect_stereotypes(text_lower, associations)
        
        # Combine scores (weighted average)
        final_score = 0.7 * bias_score + 0.3 * stereotype_score
        
        # Determine bias direction
        if final_score > 0.1:
            bias_direction = "MALE"
        elif final_score < -0.1:
            bias_direction = "FEMALE"
        else:
            bias_direction = "NEUTRAL"
        
        return {
            'bias_type': 'gender',
            'male_count': male_count,
            'female_count': female_count,
            'total_gendered': total,
            'bias_score': final_score,
            'bias_direction': bias_direction,
            'bias_label': self.get_bias_label(final_score),
            'details': f"Male: {male_count}, Female: {female_count}, Associations: {len(associations)}",
            'associations': associations,  # Include detailed associations
            'context_aware': True
        }
    
    def _detect_stereotypes(self, text: str, associations: List[Dict]) -> float:
        """Detect stereotypical gender-profession associations"""
        # Known stereotypical associations
        male_stereotyped = ['doctor', 'engineer', 'ceo', 'pilot', 'programmer', 'scientist', 'mechanic']
        female_stereotyped = ['nurse', 'secretary', 'flight attendant', 'assistant', 'receptionist']
        
        male_stereotype_count = 0
        female_stereotype_count = 0
        
        for assoc in associations:
            prof = assoc['profession']
            gender = assoc['gender']
            
            # Check if association matches stereotype
            if prof in male_stereotyped and gender == 'male':
                male_stereotype_count += 1
            elif prof in female_stereotyped and gender == 'female':
                female_stereotype_count += 1
        
        total_stereotypes = male_stereotype_count + female_stereotype_count
        if total_stereotypes == 0:
            return 0.0
        
        return (male_stereotype_count - female_stereotype_count) / total_stereotypes


class AgeBiasDetector(BiasDetector):
    """Detect age bias using contextual descriptor-age associations"""
    
    YOUNG_KEYWORDS = ['young', 'youth', 'teen', 'teenage', 'adolescent', 'millennial', 
                     'gen z', 'junior', 'inexperienced', 'energetic', 'fresh']
    OLD_KEYWORDS = ['old', 'elderly', 'senior', 'aged', 'mature', 'retired', 
                   'boomer', 'veteran', 'experienced', 'seasoned', 'ancient']
    
    # Positive and negative descriptors to check for stereotypes
    POSITIVE_DESCRIPTORS = ['innovative', 'energetic', 'creative', 'adaptive', 'quick', 
                           'skilled', 'wise', 'experienced', 'reliable', 'knowledgeable']
    NEGATIVE_DESCRIPTORS = ['slow', 'outdated', 'confused', 'stubborn', 'resistant',
                           'naive', 'immature', 'irresponsible', 'unreliable', 'inexperienced']
    
    def __init__(self):
        super().__init__('age')
        
    def detect(self, text: str) -> Dict:
        """Detect age bias through contextual analysis"""
        text_lower = text.lower()
        sentences = re.split(r'[.!?]+', text)
        
        # Count age-related keywords
        young_count = sum(len(re.findall(r'\b' + k + r'\b', text_lower)) 
                         for k in self.YOUNG_KEYWORDS)
        old_count = sum(len(re.findall(r'\b' + k + r'\b', text_lower)) 
                       for k in self.OLD_KEYWORDS)
        
        # Analyze age-descriptor associations (CONTEXTUAL ANALYSIS)
        associations = []
        stereotype_score = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if not sentence_lower:
                continue
            
            # Check for young keywords with descriptors
            has_young = any(young_word in sentence_lower for young_word in self.YOUNG_KEYWORDS)
            has_old = any(old_word in sentence_lower for old_word in self.OLD_KEYWORDS)
            
            if has_young:
                # Check sentiment towards young people
                has_positive = any(desc in sentence_lower for desc in self.POSITIVE_DESCRIPTORS)
                has_negative = any(desc in sentence_lower for desc in self.NEGATIVE_DESCRIPTORS)
                
                if has_positive:
                    associations.append({'age': 'young', 'sentiment': 'positive', 'sentence': sentence[:100]})
                    # Positive association with young is common, slight bias
                    stereotype_score -= 0.1
                if has_negative:
                    associations.append({'age': 'young', 'sentiment': 'negative', 'sentence': sentence[:100]})
                    # Negative stereotypes about young (e.g., "young and inexperienced")
                    if any(neg in sentence_lower for neg in ['inexperienced', 'naive', 'immature', 'irresponsible']):
                        stereotype_score += 0.3
            
            if has_old:
                # Check sentiment towards old people
                has_positive = any(desc in sentence_lower for desc in self.POSITIVE_DESCRIPTORS)
                has_negative = any(desc in sentence_lower for desc in self.NEGATIVE_DESCRIPTORS)
                
                if has_positive:
                    associations.append({'age': 'old', 'sentiment': 'positive', 'sentence': sentence[:100]})
                    # Positive association with elderly reduces bias
                    stereotype_score += 0.1
                if has_negative:
                    associations.append({'age': 'old', 'sentiment': 'negative', 'sentence': sentence[:100]})
                    # Negative stereotypes about elderly (e.g., "elderly and slow")
                    if any(neg in sentence_lower for neg in ['slow', 'outdated', 'confused', 'stubborn', 'resistant']):
                        stereotype_score -= 0.3
        
        # Calculate contextual bias score
        total = young_count + old_count
        basic_score = (young_count - old_count) / total if total > 0 else 0.0
        
        # Weight stereotypes more heavily
        final_score = 0.3 * basic_score + 0.7 * stereotype_score
        
        # Clamp score to [-1, 1]
        final_score = max(-1.0, min(1.0, final_score))
        
        # Determine bias direction
        if final_score > 0.1:
            bias_direction = "YOUTH"
        elif final_score < -0.1:
            bias_direction = "ELDERLY"
        else:
            bias_direction = "NEUTRAL"
        
        return {
            'bias_type': 'age',
            'young_count': young_count,
            'old_count': old_count,
            'total_age_mentions': total,
            'bias_score': final_score,
            'bias_direction': bias_direction,
            'bias_label': self.get_bias_label(final_score),
            'details': f"Youth-related: {young_count}, Elderly-related: {old_count}, Associations: {len(associations)}",
            'associations': associations,
            'context_aware': True
        }


class SocioeconomicBiasDetector(BiasDetector):
    """Detect socioeconomic/class bias through contextual sentiment analysis"""
    
    WEALTHY_KEYWORDS = ['rich', 'wealthy', 'affluent', 'elite', 'privileged', 'luxury',
                       'expensive', 'exclusive', 'upper class', 'prosperous', 'well-off']
    POOR_KEYWORDS = ['poor', 'broke', 'poverty', 'homeless', 'disadvantaged', 'struggling',
                    'cheap', 'affordable', 'working class', 'low income', 'underprivileged']
    
    # Descriptors to check for stereotypical associations
    POSITIVE_TRAITS = ['successful', 'smart', 'educated', 'hardworking', 'talented', 
                      'intelligent', 'capable', 'accomplished']
    NEGATIVE_TRAITS = ['lazy', 'uneducated', 'criminal', 'dangerous', 'irresponsible',
                      'dependent', 'undeserving', 'problematic']
    
    def __init__(self):
        super().__init__('socioeconomic')
        
    def detect(self, text: str) -> Dict:
        """Detect socioeconomic bias through contextual analysis"""
        text_lower = text.lower()
        sentences = re.split(r'[.!?]+', text)
        
        # Count socioeconomic keywords
        wealthy_count = sum(len(re.findall(r'\b' + k.replace(' ', r'\s+') + r'\b', text_lower)) 
                           for k in self.WEALTHY_KEYWORDS)
        poor_count = sum(len(re.findall(r'\b' + k.replace(' ', r'\s+') + r'\b', text_lower)) 
                        for k in self.POOR_KEYWORDS)
        
        # Analyze class-trait associations (CONTEXTUAL ANALYSIS)
        associations = []
        stereotype_score = 0
        
        for sentence in sentences:
            sentence = sentence.lower().strip()
            if not sentence:
                continue
            
            # Check wealthy keywords with trait associations
            for wealthy_word in self.WEALTHY_KEYWORDS:
                if wealthy_word in sentence:
                    has_positive = any(trait in sentence for trait in self.POSITIVE_TRAITS)
                    has_negative = any(trait in sentence for trait in self.NEGATIVE_TRAITS)
                    
                    if has_positive:
                        associations.append({'class': 'wealthy', 'trait': 'positive', 'sentence': sentence[:100]})
                        # Stereotype: wealthy = successful/smart
                        stereotype_score += 0.3
                        wealthy_count += 1
                    elif has_negative:
                        associations.append({'class': 'wealthy', 'trait': 'negative', 'sentence': sentence[:100]})
            
            # Check poor keywords with trait associations
            for poor_word in self.POOR_KEYWORDS:
                if poor_word in sentence:
                    has_positive = any(trait in sentence for trait in self.POSITIVE_TRAITS)
                    has_negative = any(trait in sentence for trait in self.NEGATIVE_TRAITS)
                    
                    if has_positive:
                        associations.append({'class': 'poor', 'trait': 'positive', 'sentence': sentence[:100]})
                    elif has_negative:
                        associations.append({'class': 'poor', 'trait': 'negative', 'sentence': sentence[:100]})
                        # Stereotype: poor = lazy/uneducated
                        stereotype_score -= 0.3
                        poor_count += 1
        
        # Calculate contextual bias score
        total = wealthy_count + poor_count
        basic_score = (wealthy_count - poor_count) / total if total > 0 else 0.0
        
        # Combine with stereotype detection
        final_score = 0.6 * basic_score + 0.4 * stereotype_score
        
        # Determine bias direction
        if final_score > 0.1:
            bias_direction = "WEALTHY"
        elif final_score < -0.1:
            bias_direction = "POOR"
        else:
            bias_direction = "NEUTRAL"
        
        return {
            'bias_type': 'socioeconomic',
            'wealthy_count': wealthy_count,
            'poor_count': poor_count,
            'total_class_mentions': total,
            'bias_score': final_score,
            'bias_direction': bias_direction,
            'bias_label': self.get_bias_label(final_score),
            'details': f"Wealthy-related: {wealthy_count}, Poor-related: {poor_count}, Associations: {len(associations)}",
            'associations': associations,
            'context_aware': True
        }


class RegionalBiasDetector(BiasDetector):
    """Detect regional/geographic bias"""
    
    WESTERN_KEYWORDS = ['american', 'european', 'western', 'developed', 'modern', 
                       'advanced', 'first world', 'metropolitan', 'urban', 'cosmopolitan']
    EASTERN_KEYWORDS = ['asian', 'african', 'eastern', 'developing', 'traditional',
                       'third world', 'rural', 'provincial', 'remote', 'underdeveloped']
    
    def __init__(self):
        super().__init__('regional')
        
    def detect(self, text: str) -> Dict:
        """Detect regional bias in text"""
        text_lower = text.lower()
        
        # Count regional keywords
        western_count = sum(len(re.findall(r'\b' + k.replace(' ', r'\s+') + r'\b', text_lower)) 
                           for k in self.WESTERN_KEYWORDS)
        eastern_count = sum(len(re.findall(r'\b' + k.replace(' ', r'\s+') + r'\b', text_lower)) 
                           for k in self.EASTERN_KEYWORDS)
        
        # Calculate bias score
        total = western_count + eastern_count
        bias_score = (western_count - eastern_count) / total if total > 0 else 0.0
        
        # Determine bias direction
        if bias_score > 0.1:
            bias_direction = "WESTERN"
        elif bias_score < -0.1:
            bias_direction = "EASTERN/DEVELOPING"
        else:
            bias_direction = "NEUTRAL"
        
        return {
            'bias_type': 'regional',
            'western_count': western_count,
            'eastern_count': eastern_count,
            'total_regional_mentions': total,
            'bias_score': bias_score,
            'bias_direction': bias_direction,
            'bias_label': self.get_bias_label(bias_score),
            'details': f"Western-related: {western_count}, Eastern/Developing-related: {eastern_count}"
        }


class SentimentBiasDetector(BiasDetector):
    """Detect sentiment bias (positive vs negative tone)"""
    
    POSITIVE_KEYWORDS = ['excellent', 'great', 'amazing', 'wonderful', 'fantastic', 'good',
                        'better', 'best', 'success', 'happy', 'love', 'perfect', 'brilliant']
    NEGATIVE_KEYWORDS = ['terrible', 'bad', 'awful', 'horrible', 'poor', 'worst', 'fail',
                        'failure', 'sad', 'hate', 'wrong', 'problem', 'difficult']
    
    def __init__(self):
        super().__init__('sentiment')
        
    def detect(self, text: str) -> Dict:
        """Detect sentiment bias in text"""
        text_lower = text.lower()
        
        # Count sentiment keywords
        positive_count = sum(len(re.findall(r'\b' + k + r'\b', text_lower)) 
                            for k in self.POSITIVE_KEYWORDS)
        negative_count = sum(len(re.findall(r'\b' + k + r'\b', text_lower)) 
                            for k in self.NEGATIVE_KEYWORDS)
        
        # Calculate bias score
        total = positive_count + negative_count
        bias_score = (positive_count - negative_count) / total if total > 0 else 0.0
        
        # Determine bias direction
        if bias_score > 0.1:
            bias_direction = "POSITIVE"
        elif bias_score < -0.1:
            bias_direction = "NEGATIVE"
        else:
            bias_direction = "NEUTRAL"
        
        return {
            'bias_type': 'sentiment',
            'positive_count': positive_count,
            'negative_count': negative_count,
            'total_sentiment_words': total,
            'bias_score': bias_score,
            'bias_direction': bias_direction,
            'bias_label': self.get_bias_label(bias_score),
            'details': f"Positive: {positive_count}, Negative: {negative_count}"
        }


class MultiBiasDetector:
    """Detect multiple types of bias in text"""
    
    def __init__(self, bias_types: List[str] = None):
        """
        Initialize multi-bias detector
        
        Args:
            bias_types: List of bias types to detect. 
                       If None, detects all types: ['gender', 'age', 'socioeconomic', 'regional', 'sentiment']
        """
        if bias_types is None:
            bias_types = ['gender', 'age', 'socioeconomic', 'regional', 'sentiment']
        
        self.detectors = {}
        for bias_type in bias_types:
            if bias_type == 'gender':
                self.detectors['gender'] = GenderBiasDetector()
            elif bias_type == 'age':
                self.detectors['age'] = AgeBiasDetector()
            elif bias_type == 'socioeconomic':
                self.detectors['socioeconomic'] = SocioeconomicBiasDetector()
            elif bias_type == 'regional':
                self.detectors['regional'] = RegionalBiasDetector()
            elif bias_type == 'sentiment':
                self.detectors['sentiment'] = SentimentBiasDetector()
    
    def detect_all(self, text: str) -> Dict[str, Dict]:
        """Detect all configured bias types in text"""
        results = {}
        for bias_type, detector in self.detectors.items():
            results[bias_type] = detector.detect(text)
        return results
    
    def detect_single(self, text: str, bias_type: str) -> Dict:
        """Detect a single bias type in text"""
        if bias_type in self.detectors:
            return self.detectors[bias_type].detect(text)
        else:
            raise ValueError(f"Unknown bias type: {bias_type}")
    
    def get_summary(self, text: str) -> Dict:
        """Get summary of all bias detections"""
        results = self.detect_all(text)
        
        summary = {
            'text_length': len(text),
            'total_biases_detected': sum(1 for r in results.values() if abs(r['bias_score']) > 0.1),
            'bias_results': results,
            'overall_bias_level': 'LOW'
        }
        
        # Determine overall bias level
        avg_bias = sum(abs(r['bias_score']) for r in results.values()) / len(results)
        if avg_bias > 0.3:
            summary['overall_bias_level'] = 'HIGH'
        elif avg_bias > 0.15:
            summary['overall_bias_level'] = 'MODERATE'
        
        return summary


# Helper functions for backward compatibility
def count_pronouns(text: str) -> Tuple[int, int]:
    """Legacy function for gender bias detection"""
    detector = GenderBiasDetector()
    result = detector.detect(text)
    return result['male_count'], result['female_count']


def calculate_bias_score(male_count: int, female_count: int) -> float:
    """Legacy function for gender bias score calculation"""
    total = male_count + female_count
    return (male_count - female_count) / total if total > 0 else 0.0


def get_bias_label(bias_score: float) -> str:
    """Legacy function for bias label"""
    if bias_score > 0.5:
        return "STRONG MALE BIAS"
    elif bias_score > 0.1:
        return "Moderate male bias"
    elif bias_score < -0.5:
        return "STRONG FEMALE BIAS"
    elif bias_score < -0.1:
        return "Moderate female bias"
    else:
        return "Balanced/Neutral"


if __name__ == "__main__":
    # Test the multi-bias detector
    test_text = """
    The young doctor said he would help. The elderly nurse was experienced.
    The wealthy businessman lived in an urban American city. It was excellent.
    """
    
    detector = MultiBiasDetector()
    summary = detector.get_summary(test_text)
    
    print("=" * 70)
    print("MULTI-BIAS DETECTION TEST")
    print("=" * 70)
    print(f"\nText: {test_text.strip()}\n")
    print(f"Overall Bias Level: {summary['overall_bias_level']}")
    print(f"Total Biases Detected: {summary['total_biases_detected']}\n")
    
    for bias_type, result in summary['bias_results'].items():
        print(f"{bias_type.upper()} BIAS:")
        print(f"  Score: {result['bias_score']:+.3f}")
        print(f"  Direction: {result['bias_direction']}")
        print(f"  Label: {result['bias_label']}")
        print(f"  Details: {result['details']}")
        print()
