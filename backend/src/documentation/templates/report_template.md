Video Analysis Report: {{ job_id }}
Generated on: {{ generation_date }}

1. Summary
Video Duration: {{ summary.duration_seconds | round(2) }} seconds

Total Utterances: {{ summary.total_utterances }}

Detected Topics: {{ summary.total_topics }}

Analyzed Frames: {{ summary.total_frames_analyzed }}

2. Topic Breakdown
{% for topic in topics %}

Topic {{ loop.index }}: {{ topic.topic_name }}
Summary: {{ topic.summary or 'No summary available.' }}

Associated Utterances:
{% for utterance_idx in topic.utterance_indices %}

({{ utterances[utterance_idx].start_time | round(2) }}s - {{ utterances[utterance_idx].end_time | round(2) }}s): {{ utterances[utterance_idx].text }}
{% endfor %}

{% endfor %}

3. Visual Analysis Highlights
{% for analysis in visual_analyses %}

Frame: {{ analysis.frame_id }} ({{ analysis.screen_type }})
Description:

{{ analysis.description }}

Detected Elements:
{% if analysis.detected_elements %}
| Type         | Content                               | Confidence |
|--------------|---------------------------------------|------------|
{% for element in analysis.detected_elements %}
| {{ element.type }} | {{ element.content | truncate(50) }} | {{ "%.2f"|format(element.confidence) }}    |
{% endfor %}
{% else %}
No significant elements were detected in this frame.
{% endif %}

{% endfor %}

4. Full Transcript
{% for utterance in utterances %}

[{{ utterance.start_time | round(2) }}s] {{ utterance.text }}

Summary: {{ utterance.summary or 'N/A' }}
{% endfor %}