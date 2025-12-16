#!/usr/bin/env python3
"""
Generate WordNet-based synonyms for movie/TV search domain.
Extends the existing synonyms.txt with knowledge from WordNet.
"""

from nltk.corpus import wordnet as wn
from collections import defaultdict

# Define key terms relevant to movie/TV domain that we want to expand with WordNet
DOMAIN_TERMS = {
    # Movie/TV related nouns
    'nouns': [
        'movie', 'film', 'cinema', 'theater', 'actor', 'actress', 'director',
        'producer', 'writer', 'script', 'screenplay', 'plot', 'story', 'narrative',
        'character', 'hero', 'villain', 'protagonist', 'antagonist', 'scene',
        'episode', 'series', 'season', 'sequel', 'prequel', 'remake', 'adaptation',
        'genre', 'drama', 'comedy', 'tragedy', 'thriller', 'horror', 'mystery',
        'romance', 'adventure', 'fantasy', 'documentary', 'animation', 'cartoon',
        'soundtrack', 'score', 'music', 'dialogue', 'monologue', 'performance',
        'audience', 'viewer', 'spectator', 'critic', 'review', 'rating',
        'award', 'prize', 'nomination', 'premiere', 'release', 'screening',
        'blockbuster', 'masterpiece', 'classic', 'hit', 'flop', 'bomb',
        'cast', 'crew', 'ensemble', 'star', 'celebrity', 'icon',
        'cinematography', 'photography', 'lighting', 'editing', 'montage',
        'costume', 'makeup', 'wardrobe', 'set', 'location', 'studio',
        'battle', 'war', 'conflict', 'fight', 'chase', 'escape',
        'love', 'friendship', 'family', 'betrayal', 'revenge', 'redemption',
        'journey', 'quest', 'mission', 'heist', 'investigation', 'mystery'
    ],
    # Adjectives for describing movies/shows
    'adjectives': [
        'exciting', 'boring', 'thrilling', 'scary', 'funny', 'hilarious',
        'dramatic', 'emotional', 'touching', 'moving', 'heartfelt', 'sad',
        'happy', 'dark', 'light', 'intense', 'powerful', 'weak',
        'brilliant', 'excellent', 'great', 'good', 'bad', 'terrible',
        'awful', 'amazing', 'fantastic', 'outstanding', 'mediocre', 'average',
        'gripping', 'captivating', 'engaging', 'compelling', 'riveting',
        'predictable', 'surprising', 'shocking', 'unexpected', 'original',
        'creative', 'innovative', 'unique', 'fresh', 'new', 'old',
        'classic', 'modern', 'contemporary', 'vintage', 'retro', 'nostalgic',
        'violent', 'brutal', 'graphic', 'gory', 'bloody', 'disturbing',
        'romantic', 'sentimental', 'heartwarming', 'uplifting', 'inspiring',
        'depressing', 'melancholic', 'tragic', 'hopeful', 'optimistic',
        'realistic', 'authentic', 'believable', 'unrealistic', 'absurd',
        'intelligent', 'smart', 'clever', 'witty', 'dumb', 'stupid',
        'fast', 'slow', 'quick', 'rapid', 'sluggish', 'tedious',
        'beautiful', 'gorgeous', 'stunning', 'ugly', 'hideous',
        'suspenseful', 'tense', 'nerve-wracking', 'relaxing', 'calming',
        'action-packed', 'explosive', 'dynamic', 'static', 'stagnant',
        'epic', 'grand', 'magnificent', 'spectacular', 'impressive',
        'entertaining', 'enjoyable', 'fun', 'amusing', 'delightful',
        'confusing', 'complex', 'complicated', 'simple', 'straightforward',
        'mysterious', 'enigmatic', 'puzzling', 'intriguing', 'curious',
        'creepy', 'eerie', 'spooky', 'haunting', 'chilling', 'terrifying',
        'legendary', 'iconic', 'memorable', 'forgettable', 'bland', 'generic'
    ],
    # Verbs related to movie actions/experiences
    'verbs': [
        'watch', 'see', 'view', 'stream', 'download', 'play',
        'act', 'perform', 'portray', 'depict', 'represent', 'embody',
        'direct', 'produce', 'write', 'create', 'develop', 'adapt',
        'film', 'shoot', 'record', 'capture', 'edit', 'cut',
        'recommend', 'suggest', 'advise', 'endorse', 'promote',
        'review', 'critique', 'analyze', 'evaluate', 'rate', 'rank',
        'enjoy', 'love', 'hate', 'dislike', 'appreciate', 'admire',
        'laugh', 'cry', 'scream', 'gasp', 'cheer', 'applaud',
        'fight', 'battle', 'chase', 'escape', 'survive', 'die',
        'investigate', 'discover', 'reveal', 'uncover', 'expose',
        'transform', 'evolve', 'change', 'grow', 'develop', 'mature'
    ]
}

def get_wordnet_synonyms(word, pos=None):
    """Get synonyms for a word from WordNet."""
    synonyms = set()
    
    # Map to WordNet POS tags
    pos_map = {
        'nouns': wn.NOUN,
        'adjectives': wn.ADJ,
        'verbs': wn.VERB
    }
    
    wn_pos = pos_map.get(pos)
    
    if wn_pos:
        synsets = wn.synsets(word, pos=wn_pos)
    else:
        synsets = wn.synsets(word)
    
    for synset in synsets:
        for lemma in synset.lemmas():
            synonym = lemma.name().replace('_', ' ').lower()
            if synonym != word.lower() and len(synonym) > 2:
                synonyms.add(synonym)
    
    return synonyms

def generate_synonym_groups():
    """Generate synonym groups from WordNet for domain terms."""
    synonym_groups = defaultdict(set)
    
    for pos, terms in DOMAIN_TERMS.items():
        for term in terms:
            synonyms = get_wordnet_synonyms(term, pos)
            if synonyms:
                # Add the original term and its synonyms to the group
                synonym_groups[term].add(term)
                synonym_groups[term].update(synonyms)
    
    return synonym_groups

def filter_relevant_synonyms(synonym_groups):
    """Filter and clean synonym groups to keep only relevant ones."""
    filtered_groups = {}
    
    for main_term, synonyms in synonym_groups.items():
        # Remove very short or very long synonyms
        cleaned = {s for s in synonyms if 2 < len(s) < 30}
        
        # Only keep groups with at least 2 synonyms
        if len(cleaned) >= 2:
            # Sort and limit to top synonyms to avoid noise
            sorted_syns = sorted(cleaned)[:8]  # Keep up to 8 synonyms per term
            filtered_groups[main_term] = sorted_syns
    
    return filtered_groups

def format_solr_synonyms(synonym_groups):
    """Format synonyms in Solr synonym format."""
    lines = []
    
    # Group by category for readability
    seen = set()
    
    for main_term in sorted(synonym_groups.keys()):
        if main_term in seen:
            continue
        
        synonyms = synonym_groups[main_term]
        # Mark all synonyms as seen to avoid duplicates
        for s in synonyms:
            seen.add(s)
        
        if len(synonyms) >= 2:
            line = ', '.join(synonyms)
            lines.append(line)
    
    return lines

def main():
    print("Generating WordNet synonyms for movie/TV domain...")
    
    # Generate synonym groups
    synonym_groups = generate_synonym_groups()
    print(f"Found {len(synonym_groups)} terms with synonyms")
    
    # Filter to keep only relevant synonyms
    filtered_groups = filter_relevant_synonyms(synonym_groups)
    print(f"Filtered to {len(filtered_groups)} useful synonym groups")
    
    # Format for Solr
    synonym_lines = format_solr_synonyms(filtered_groups)
    
    # Print the WordNet synonyms section
    print("\n# WORDNET KNOWLEDGE BASE SYNONYMS")
    print("# Auto-generated from WordNet for movie/TV domain\n")
    
    # Group by category
    noun_lines = []
    adj_lines = []
    verb_lines = []
    
    for term in sorted(filtered_groups.keys()):
        synonyms = filtered_groups[term]
        line = ', '.join(synonyms)
        
        if term in DOMAIN_TERMS['nouns']:
            noun_lines.append(line)
        elif term in DOMAIN_TERMS['adjectives']:
            adj_lines.append(line)
        elif term in DOMAIN_TERMS['verbs']:
            verb_lines.append(line)
    
    output_lines = []
    
    output_lines.append("\n# WORDNET KNOWLEDGE BASE - NOUNS")
    output_lines.extend(noun_lines)
    
    output_lines.append("\n# WORDNET KNOWLEDGE BASE - ADJECTIVES")
    output_lines.extend(adj_lines)
    
    output_lines.append("\n# WORDNET KNOWLEDGE BASE - VERBS")
    output_lines.extend(verb_lines)
    
    # Print output
    for line in output_lines:
        print(line)
    
    # Return the lines for file writing
    return output_lines

if __name__ == "__main__":
    output = main()
    
    # Write to file (append to existing synonyms.txt)
    output_path = "/home/nhanho/Masters/PRI/PRI/Milestone_3/synonyms.txt"
    
    with open(output_path, 'a') as f:
        f.write("\n")
        for line in output:
            f.write(line + "\n")
    
    print(f"\nSynonyms appended to {output_path}")
