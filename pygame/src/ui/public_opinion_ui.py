'''
Public Opinion UI Components - Display public opinion metrics and media stories.

This module provides UI components for showing public opinion data in the game interface.
'''

import pygame
from typing import Tuple, List

from src.features.public_opinion import PublicOpinion, OpinionCategory


def get_opinion_color(value: float) -> Tuple[int, int, int]:
    '''Get color for an opinion value (0-100 scale).'''
    if value >= 70:
        return (0, 180, 0)  # Green for good
    elif value >= 50:
        return (200, 200, 0)  # Yellow for neutral
    elif value >= 30:
        return (255, 140, 0)  # Orange for concerning
    else:
        return (255, 60, 60)  # Red for bad


def get_trend_symbol(trend: str) -> str:
    '''Get symbol for opinion trend.'''
    if trend == 'rising':
        return '?'
    elif trend == 'falling':
        return '?'
    else:
        return '?'


def draw_public_opinion_panel(screen: pygame.Surface, public_opinion: PublicOpinion, 
                             font: pygame.font.Font, small_font: pygame.font.Font,
                             position: Tuple[int, int], width: int = 300) -> int:
    '''
    Draw public opinion panel showing current metrics and trends.
    
    Returns: Height of the drawn panel
    '''
    x, y = position
    line_height = 20
    current_y = y
    
    # Panel title
    title_color = (255, 255, 255)
    title_text = font.render('Public Opinion', True, title_color)
    screen.blit(title_text, (x, current_y))
    current_y += line_height + 5
    
    # Draw opinion metrics
    metrics = [
        ('General Sentiment', public_opinion.general_sentiment, OpinionCategory.GENERAL_SENTIMENT),
        ('Trust in Your Lab', public_opinion.trust_in_player, OpinionCategory.TRUST_IN_PLAYER),
        ('AI Safety Awareness', public_opinion.ai_safety_awareness, OpinionCategory.AI_SAFETY_AWARENESS),
        ('Media Attention', public_opinion.media_attention, OpinionCategory.MEDIA_ATTENTION)
    ]
    
    for name, value, category in metrics:
        color = get_opinion_color(value)
        trend = public_opinion.get_trend(category)
        trend_symbol = get_trend_symbol(trend)
        
        # Draw metric name
        name_text = small_font.render(f'{name}:', True, (200, 200, 200))
        screen.blit(name_text, (x, current_y))
        
        # Draw value and trend
        value_text = f'{value:.1f}% {trend_symbol}'
        value_surface = small_font.render(value_text, True, color)
        screen.blit(value_surface, (x + 120, current_y))
        
        # Draw progress bar
        bar_x = x + 200
        bar_y = current_y + 5
        bar_width = 80
        bar_height = 10
        
        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        
        # Fill
        fill_width = int((value / 100) * bar_width)
        if fill_width > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)
        
        current_y += line_height
    
    return current_y - y


def draw_media_stories_panel(screen: pygame.Surface, public_opinion: PublicOpinion,
                           font: pygame.font.Font, small_font: pygame.font.Font,
                           position: Tuple[int, int], width: int = 400, 
                           max_stories: int = 5) -> int:
    '''
    Draw media stories panel showing active stories.
    
    Returns: Height of the drawn panel
    '''
    x, y = position
    line_height = 18
    current_y = y
    
    # Panel title
    title_color = (255, 255, 255)
    title_text = font.render('Media Coverage', True, title_color)
    screen.blit(title_text, (x, current_y))
    current_y += line_height + 5
    
    # Draw active stories
    if not public_opinion.active_stories:
        no_stories_text = small_font.render('No major stories currently active.', True, (150, 150, 150))
        screen.blit(no_stories_text, (x, current_y))
        current_y += line_height
    else:
        # Sort stories by creation time (newest first)
        sorted_stories = sorted(public_opinion.active_stories, 
                              key=lambda s: s.created_turn, reverse=True)
        
        for i, story in enumerate(sorted_stories[:max_stories]):
            if i >= max_stories:
                break
            
            # Story type icon
            type_icons = {
                'breakthrough': '[ROCKET]',
                'scandal': '[WARNING]?',
                'human_interest': '?',
                'policy': '??',
                'safety_concern': '[SHIELD]?',
                'industry_news': '?'
            }
            icon = type_icons.get(story.story_type.value, '[NEWS]')
            
            # Story headline (truncated if too long)
            max_headline_length = 45
            headline = story.headline
            if len(headline) > max_headline_length:
                headline = headline[:max_headline_length-3] + '...'
            
            # Get remaining turns
            remaining = story.get_remaining_turns(public_opinion.opinion_history['general_sentiment'].__len__())
            remaining_text = f'({remaining}t)' if remaining > 0 else '(exp)'
            
            story_text = f'{icon} {headline} {remaining_text}'
            
            # Color based on story type
            if story.story_type.value == 'scandal':
                color = (255, 100, 100)
            elif story.story_type.value == 'breakthrough':
                color = (100, 255, 100)
            else:
                color = (200, 200, 200)
            
            story_surface = small_font.render(story_text, True, color)
            screen.blit(story_surface, (x, current_y))
            current_y += line_height
    
    return current_y - y


def draw_opinion_summary(screen: pygame.Surface, public_opinion: PublicOpinion,
                        font: pygame.font.Font, position: Tuple[int, int], 
                        width: int = 500) -> int:
    '''
    Draw a text summary of the current public opinion state.
    
    Returns: Height of the drawn text
    '''
    x, y = position
    line_height = 20
    
    summary = public_opinion.get_summary()
    
    # Word wrap the summary
    words = summary.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, (255, 255, 255))
        
        if test_surface.get_width() <= width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)  # Single word too long, add anyway
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw the lines
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, (200, 200, 200))
        screen.blit(line_surface, (x, y + i * line_height))
    
    return len(lines) * line_height


def draw_compact_opinion_display(screen: pygame.Surface, public_opinion: PublicOpinion,
                                small_font: pygame.font.Font, position: Tuple[int, int]) -> int:
    '''
    Draw a compact single-line opinion display for minimal UI space.
    
    Returns: Width of the drawn display
    '''
    x, y = position
    
    # Get key metrics
    sentiment = public_opinion.general_sentiment
    trust = public_opinion.trust_in_player
    
    # Create compact display
    get_opinion_color(sentiment)
    get_opinion_color(trust)
    
    # Format: 'Opinion: 65% | Trust: 72%'
    text = f'Opinion: {sentiment:.0f}% | Trust: {trust:.0f}%'
    
    # Draw with average color
    avg_value = (sentiment + trust) / 2
    avg_color = get_opinion_color(avg_value)
    
    text_surface = small_font.render(text, True, avg_color)
    screen.blit(text_surface, (x, y))
    
    return text_surface.get_width()


def get_opinion_effects_on_gameplay(public_opinion: PublicOpinion) -> List[str]:
    '''
    Get list of current gameplay effects from public opinion.
    
    Returns list of effect descriptions.
    '''
    effects = []
    
    # High trust effects
    if public_opinion.trust_in_player >= 70:
        effects.append('? +20% funding from high public trust')
        effects.append('? -10% regulatory pressure')
        effects.append('? Easier researcher recruitment')
    
    # Low trust effects  
    elif public_opinion.trust_in_player <= 30:
        effects.append('? -30% funding availability')
        effects.append('? +20% regulatory pressure')
        effects.append('[WARNING]? Competitors can use public concern against you')
    
    # High safety awareness effects
    if public_opinion.ai_safety_awareness >= 70:
        effects.append('[SHIELD]? Safety research generates more reputation')
        effects.append('[WARNING]? Capabilities research generates suspicion')
        effects.append('? Unlock 'Public Safety Advocate' funding')
    
    # High media attention effects
    if public_opinion.media_attention >= 50:
        effects.append('? Your actions have amplified public impact')
        effects.append('? Increased scrutiny of your lab's activities')
    
    return effects