import asyncio
from loguru import logger

class GeminiAnalyzer:
    def __init__(self, api_key: str, reputation_db_manager):
        self.api_key = api_key
        self.reputation_db_manager = reputation_db_manager
        self.recent_logs = []

    def update_api_key(self, new_key: str):
        self.api_key = new_key
        logger.info("Gemini API key updated.")

    async def analyze_token(self, token_data: dict) -> float:
        logger.info(f"Performing AI analysis for token: {token_data.get('mint_address')}")
        risk_score = self._simulate_ai_analysis(token_data)
        wallet_id = token_data.get('mint_address')
        ip_publique = "192.168.1.1"
        tags = "new_token, untested"
        comportement = f"AI analyzed, score: {risk_score}"
        self.reputation_db_manager.add_entry(wallet_id, ip_publique, tags, comportement, risk_score)

        log_entry = {
            "timestamp": asyncio.get_event_loop().time(),
            "token": token_data.get('mint_address'),
            "risk_score": risk_score,
            "details": "Simulated AI analysis"
        }
        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > 100:
            self.recent_logs.pop(0)

        return risk_score

    def _create_analysis_prompt(self, token_data: dict) -> str:
        # Construct a detailed prompt for Gemini based on token_data
        prompt = f"Analyze the following Solana token data for potential risks and provide a confidence score (0.0 to 1.0) indicating its trustworthiness. Also, identify any suspicious patterns related to creator activity, liquidity, or holder distribution.\n\nToken Mint Address: {token_data.get('mint_address')}\n"
        if token_data.get('token_info'):
            prompt += f"Token Info: {token_data['token_info']}\n"
        if token_data.get('token_supply'):
            prompt += f"Token Supply: {token_data['token_supply']}\n"
        if token_data.get('token_holders'):
            prompt += f"Token Holders (partial): {token_data['token_holders']}\n"
        prompt += "\nBased on this, provide a risk score (0.0 to 1.0, where 1.0 is very trustworthy and 0.0 is very risky) and a brief explanation of your reasoning. Format your response as 'SCORE: [score]\nREASONING: [explanation]'."
        return prompt

    def _parse_gemini_response(self, response_text: str) -> float:
        # Parse the Gemini response to extract the risk score
        try:
            score_line = [line for line in response_text.split('\n') if line.startswith('SCORE:')][0]
            score = float(score_line.split(':')[1].strip())
            return max(0.0, min(1.0, score)) # Ensure score is between 0 and 1
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {response_text}. Error: {e}")
            return 0.5 # Default to neutral if parsing fails

    def _simulate_ai_analysis(self, token_data: dict) -> float:
        # Simulation passive IA: analyse les signaux historiques ou locaux
        mint_address = token_data.get('mint_address', '')
        score = 0.6 + (hash(mint_address) % 100) / 1000.0
        if token_data.get('liquidity', 0) < 3.0:
            score -= 0.3
        if token_data.get('honeypot', False):
            score -= 0.4
        if token_data.get('blacklisted', False):
            score -= 0.5
        return max(0.0, min(1.0, score))
    def export_simulation_report(self, filename: str = "gemini_simulation_report.json"):
        import json
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.recent_logs, f, ensure_ascii=False, indent=2)

    def get_recent_logs(self):
        return self.recent_logs