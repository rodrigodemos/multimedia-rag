import { renderToStaticMarkup } from "react-dom/server";
import { ChatAppResponse, getCitationFilePath } from "../../api";

export interface Citation {
    name: string;
    url: string;
}

type HtmlParsedAnswer = {
    answerHtml: string;
    citations: Citation[];
};

// Function to validate citation format and check if dataPoint starts with possible citation
function isCitationValid(contextDataPoints: any, citationCandidate: string): boolean {
    const regex = /.+\.\w{1,}(?:#\S*)?$/;
    if (!regex.test(citationCandidate)) {
        return false;
    }

    // Check if contextDataPoints is an object with a text property that is an array
    let dataPointsArray: string[];
    if (Array.isArray(contextDataPoints)) {
        dataPointsArray = contextDataPoints;
    } else if (contextDataPoints && Array.isArray(contextDataPoints.text)) {
        dataPointsArray = contextDataPoints.text;
    } else {
        return false;
    }

    const isValidCitation = dataPointsArray.some(dataPoint => {
        return dataPoint.startsWith(citationCandidate);
    });
    return isValidCitation;
}

export function parseAnswerToHtml(answer: ChatAppResponse, isStreaming: boolean, onCitationClicked: (citationFilePath: string) => void): HtmlParsedAnswer {
    const contextDataPoints = answer.context.data_points;
    const citations: Citation[] = [];

    // Trim any whitespace from the end of the answer after removing follow-up questions
    let parsedAnswer = answer.message.content.trim();

    // Omit a citation that is still being typed during streaming
    if (isStreaming) {
        let lastIndex = parsedAnswer.length;
        for (let i = parsedAnswer.length - 1; i >= 0; i--) {
            if (parsedAnswer[i] === "]") {
                break;
            } else if (parsedAnswer[i] === "[") {
                lastIndex = i;
                break;
            }
        }
        const truncatedAnswer = parsedAnswer.substring(0, lastIndex);
        parsedAnswer = truncatedAnswer;
    }
    const parts = parsedAnswer.split(/\[([^\]]+)\]/g);

    const fragments: string[] = parts.map((part, index) => {
        if (index % 2 === 0) {
            return part;
        } else {
            let name: string | null = null;
            let citationIndex: number;
            let url: string | null = null;

            const urlMatch = part.match(/\((https?:\/\/[^\s]+)\)/);
            if (urlMatch) {
                url = urlMatch[1];
                part = part.replace(urlMatch[0], "");
            } else {
                url = getCitationFilePath(part);
            }

            if (!isCitationValid(contextDataPoints, part)) {
                return `[${part}]`;
            }

            name = part;

            // Check if citation already exists
            const existingIndex = citations.findIndex(c => c.name === name && c.url === url);
            if (existingIndex !== -1) {
                citationIndex = existingIndex + 1;
            } else {
                citations.push({ name, url });
                citationIndex = citations.length;
            }

            return renderToStaticMarkup(
                <a className="supContainer" title={name} onClick={() => onCitationClicked(url)}>
                    <sup>{citationIndex}</sup>
                </a>
            );
        }
    });

    return {
        answerHtml: fragments.join(""),
        citations
    };
}
