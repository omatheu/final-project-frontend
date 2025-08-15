export async function POST(req: Request) {
  try {
    const { message } = await req.json()

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${process.env.GEMINI_API_KEY}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: `You are DEMO, an intelligent AI assistant that helps users with various tasks including:
- Creating presentations and pitch decks
- Brainstorming ideas and concepts
- Providing visual suggestions and creative solutions
- Helping with business and technical problems

You should be helpful, creative, and provide detailed responses. When appropriate, suggest visual elements or creative approaches to problems.

User message: ${message}`,
                },
              ],
            },
          ],
        }),
      },
    )

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status}`)
    }

    const data = await response.json()
    const aiResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || "Sorry, I couldn't generate a response."

    return Response.json({ response: aiResponse })
  } catch (error) {
    console.error("Error in chat API:", error)
    return Response.json({ error: "Error processing request" }, { status: 500 })
  }
}
