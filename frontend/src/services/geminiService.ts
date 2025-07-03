
import { GoogleGenAI, GenerateContentResponse, GenerateContentParameters } from "@google/genai";
import { Utterance, Topic, GeminiTopicResponse, ModelConfig } from '../types';

if (!process.env.API_KEY) {
  throw new Error("API_KEY environment variable is not set");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const parseJsonFromMarkdown = <T,>(text: string): T | null => {
  let jsonStr = text.trim();
  const fenceRegex = /^```(\w*)?\s*\n?(.*?)\n?\s*```$/s;
  const match = jsonStr.match(fenceRegex);
  if (match && match[2]) {
    jsonStr = match[2].trim();
  }
  try {
    return JSON.parse(jsonStr) as T;
  } catch (e) {
    console.error("Failed to parse JSON response:", e, "Original text:", text);
    return null;
  }
};

const buildApiConfig = (modelConfig: ModelConfig): GenerateContentParameters['config'] => {
    const config: GenerateContentParameters['config'] = {
        temperature: modelConfig.temperature,
        topP: modelConfig.topP,
        topK: modelConfig.topK,
    };

    // 'thinkingConfig' is generally for flash models.
    // Apply it only when mode is 'fastest' and a compatible model is selected.
    if (modelConfig.mode === 'fastest' && modelConfig.model.includes('flash')) {
        config.thinkingConfig = { thinkingBudget: 0 };
    }
    return config;
}

export const summarizeUtterance = async (utterance: string, modelConfig: ModelConfig): Promise<string> => {
  const prompt = `You are an expert context summarizer. Given the following utterance from a technical meeting transcript, provide a concise one-sentence summary of its core subject. Utterance: "${utterance}"`;

  try {
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: modelConfig.model,
      contents: prompt,
      config: buildApiConfig(modelConfig)
    });
    return response.text.trim();
  } catch (error) {
    console.error("Error summarizing utterance:", error);
    return "Error generating summary.";
  }
};

export const generateTopics = async (summaries: string[], modelConfig: ModelConfig): Promise<GeminiTopicResponse[] | null> => {
    const formattedSummaries = summaries.map((s, i) => `Index ${i}: ${s}`).join('\n');
    const prompt = `You are an expert in topic modeling for technical discussions. Based on the following list of indexed utterance summaries, identify 2-4 main topics. For each topic, provide a short name and list the indices of the summaries that belong to it.

    Respond ONLY with a valid JSON array of objects in the format:
    [
      {"topic": "Topic Name 1", "utterance_indices": [0, 1, 2]},
      {"topic": "Topic Name 2", "utterance_indices": [3, 4]}
    ]
    
    Summaries:
    ${formattedSummaries}`;
  
    const apiConfig = buildApiConfig(modelConfig);
    apiConfig.responseMimeType = "application/json";
  
    try {
      const response: GenerateContentResponse = await ai.models.generateContent({
        model: modelConfig.model,
        contents: prompt,
        config: apiConfig
      });
      
      return parseJsonFromMarkdown<GeminiTopicResponse[]>(response.text);

    } catch (error) {
      console.error("Error generating topics:", error);
      return [];
    }
  };
  
export const analyzeFrame = async (transcriptContext: string, frameData: { mimeType: string, data: string }, modelConfig: ModelConfig): Promise<string> => {
  const textPart = {
    text: `You are a world-class AI vision model with deep expertise in software engineering, systems engineering, and IT support. You will be given the transcript of a video segment and a frame from that segment. 
  
  Your task is to provide a highly detailed analysis of the visual elements in the frame, interpreting them within the provided technical context. Describe the literal items on screen (e.g., 'a code editor showing a JavaScript function', 'a terminal window with a docker command', 'a UML sequence diagram') and explain their significance in relation to the transcript. Be descriptive and thorough.
  
  **Transcript Context:**
  "${transcriptContext}"`
  };
  
  const imagePart = {
    inlineData: {
      mimeType: frameData.mimeType,
      data: frameData.data
    }
  };

  try {
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: modelConfig.model,
      contents: { parts: [textPart, imagePart] },
      config: buildApiConfig(modelConfig)
    });
    return response.text.trim();
  } catch (error) {
    console.error("Error analyzing frame:", error);
    return "Error generating visual analysis.";
  }
};

export const generateMarkdownReport = async (topics: Topic[], utterances: Utterance[], modelConfig: ModelConfig): Promise<string> => {
    const dataForPrompt = topics.map(topic => ({
        topicName: topic.name,
        discussionSummary: topic.utteranceIds.map(id => utterances.find(u => u.id === id)?.text).join(' '),
        visuals: topic.frames.map(frame => ({
            timestamp: frame.timestamp,
            analysis: frame.analysis
        }))
    }));

    const prompt = `You are a technical writer AI. Create a comprehensive summary report in Markdown format based on the following structured data. The report must start with a main title "# Final Analysis Report". It should then have a "## Table of Contents" section with clickable links to each topic section (e.g., "- [Topic Name](#topic-name)"). 

For each topic, create a section with a heading (e.g., "### Topic Name"). In each section, provide a brief summary of the discussion for that topic. Then, list the key visual elements identified from the video frames under a "Key Visuals" sub-heading, including their timestamps and the detailed analysis.

**Data:**
${JSON.stringify(dataForPrompt, null, 2)}`;
  
    try {
      const response: GenerateContentResponse = await ai.models.generateContent({
        model: modelConfig.model,
        contents: prompt,
        config: buildApiConfig(modelConfig)
      });
      return response.text;
    } catch (error) {
      console.error("Error generating report:", error);
      return "## Error\nCould not generate the final report.";
    }
  };