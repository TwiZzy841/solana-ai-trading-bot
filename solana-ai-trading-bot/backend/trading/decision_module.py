
from loguru import logger
import asyncio
from typing import Dict, List, Optional, Any


class DecisionModule:
    """
    Module de décision pour le trading automatique (simulation/réel).
    Gère le capital, la logique d'achat/vente, les logs, et l'intégration IA.
    """

    def log_trade(self, entry: dict, simulation: bool = True) -> None:
        """
        Enregistre chaque trade dans un fichier log distinct selon le mode (simulation ou réel).
        """
        import json
        log_file = "simulation_trades.log" if simulation else "real_trades.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture du log trade : {e}")

    def enable_real_time_simulation(self) -> None:
        """Active le mode simulation en temps réel (aucun argent réel utilisé)."""
        self.simulation_mode = True
        self.simulation_results = []
        logger.info("Mode simulation activé (aucun trade réel ne sera effectué).")

    def record_simulation_trade(self, entry: dict) -> None:
        """
        Ajoute un trade simulé à la liste et au fichier log de simulation.
        """
        self.simulation_results.append(entry)
        self.log_trade(entry, simulation=True)

    def record_real_trade(self, entry: dict) -> None:
        """
        Ajoute un trade réel au fichier log dédié.
        """
        self.log_trade(entry, simulation=False)

    def get_simulation_profit_loss(self) -> float:
        """Calcule le profit/perte total de la simulation."""
        profit = 0.0
        buy_prices = {}
        for entry in self.simulation_results:
            if entry["action"] == "buy":
                buy_prices[entry["token"]] = entry["price"]
            elif entry["action"] == "sell" and entry["token"] in buy_prices:
                profit += entry["price"] - buy_prices[entry["token"]]
        return profit

    def export_simulation_report_for_gemini(self, filename: str = "simulation_gemini.json") -> None:
        """Export des résultats de simulation pour analyse Gemini."""
        import json
        report = {
            "results": self.simulation_results,
            "profit_loss": self.get_simulation_profit_loss(),
            "parameters": {
                "buy_amount_sol": self.buy_amount_sol,
                "sell_multiplier": self.sell_multiplier
            }
        }
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"Rapport simulation exporté pour Gemini : {filename}")
        except Exception as e:
            logger.error(f"Erreur export rapport Gemini : {e}")
    def __init__(self, order_executor: Any, buy_amount_sol: float, sell_multiplier: float, simulation_mode: bool = False):
        """
        Initialise le module de décision.
        order_executor : module d'exécution des ordres (buy/sell)
        buy_amount_sol : montant à investir par trade
        sell_multiplier : multiplicateur de take profit
        simulation_mode : True pour la simulation, False pour le réel
        """
        self.order_executor = order_executor
        self.buy_amount_sol = buy_amount_sol
        self.sell_multiplier = sell_multiplier
        self.simulation_mode = simulation_mode
        self.simulation_results: List[dict] = []
        self.held_tokens: Dict[str, dict] = {} # {mint_address: {buy_price: float, buy_amount: float}}
        self.capital: float = 0.0
        self.available_capital: float = 0.0
        self.ia_hooks: List[Any] = [] # Pour brancher des modules IA/optimisation

    def set_initial_capital(self, amount: float) -> None:
        """
        Définit le capital de départ à investir (modifié via l'interface).
        """
        self.capital = float(amount)
        self.available_capital = float(amount)
        logger.info(f"Capital initial défini à {amount} SOL")

    def get_available_capital(self) -> float:
        """
        Retourne le capital disponible pour investissement.
        """
        return self.available_capital

    def update_after_trade(self, profit_or_loss: float) -> None:
        """
        Met à jour le capital disponible après chaque trade (réinvestissement automatique des gains).
        """
        self.available_capital += profit_or_loss
        if self.available_capital < 0:
            self.available_capital = 0
        logger.info(f"Capital mis à jour après trade : {self.available_capital} SOL")

    def get_next_investment_amount(self) -> float:
        """
        Calcule le montant à investir pour le prochain trade (100% du capital disponible).
        """
        return self.available_capital

    async def process_new_token_candidate(self, token_mint_address: str, current_price: float) -> None:
        """
        Analyse un nouveau token candidat et décide d'acheter ou non.
        """
        logger.info(f"Decision module received new token candidate: {token_mint_address} at price {current_price}")
        try:
            will_double = await self._predict_x2_in_10min(token_mint_address, current_price)
            if not will_double:
                logger.warning(f"Token {token_mint_address} ne devrait pas atteindre x2 dans les 10min, achat annulé.")
                return
            if self.simulation_mode:
                result = {
                    "token": token_mint_address,
                    "price": current_price,
                    "action": "buy",
                    "timestamp": asyncio.get_event_loop().time()
                }
                self.simulation_results.append(result)
                self.log_trade(result, simulation=True)
                logger.info(f"Simulation mode: buy logged for {token_mint_address}")
                return
            if token_mint_address not in self.held_tokens:
                logger.info(f"Attempting to buy {self.buy_amount_sol} SOL worth of {token_mint_address}")
                success = await self.order_executor.execute_buy(token_mint_address, self.buy_amount_sol)
                if success:
                    creator_wallets = await self._detect_creator_wallets(token_mint_address)
                    self.held_tokens[token_mint_address] = {
                        "buy_price": current_price,
                        "buy_amount": self.buy_amount_sol,
                        "creator_wallets": creator_wallets
                    }
                    logger.success(f"Successfully bought {token_mint_address}. Tracking for sale. Creator wallets: {creator_wallets}")
                    # Hook IA/logs après achat réel
                    self.record_real_trade({
                        "token": token_mint_address,
                        "price": current_price,
                        "action": "buy",
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    for hook in self.ia_hooks:
                        try:
                            hook.on_trade("buy", token_mint_address, current_price)
                        except Exception as e:
                            logger.warning(f"Erreur hook IA après achat : {e}")
                else:
                    logger.error(f"Failed to buy {token_mint_address}.")
            else:
                logger.info(f"Already holding {token_mint_address}, skipping buy.")
        except Exception as e:
            logger.error(f"Erreur process_new_token_candidate : {e}")
    async def _predict_x2_in_10min(self, token_mint_address: str, current_price: float) -> bool:
        """Prédit si le token peut atteindre x2 dans les 10min en moins de 800ms (ultra-rapide)."""
        import random, time, asyncio
        start = time.time()
        # Recherche dans la base de données historique
        score = 0.5
        try:
            # Supposons qu'on ait accès à self.db_manager (à adapter selon l'architecture)
            if hasattr(self, 'db_manager'):
                db = self.db_manager
                # Exemple: requête sur les tokens similaires ayant fait x2 en 10min
                similar_tokens = db.get_tokens_with_x2_in_10min(token_mint_address)
                if similar_tokens:
                    score += 0.4
                else:
                    score -= 0.2
        except Exception as e:
            logger.warning(f"Erreur accès base de données pour la prédiction: {e}")
        # Heuristique simple : nom, supply, holders, blacklist
        if "good" in token_mint_address.lower():
            score += 0.2
        if "scam" in token_mint_address.lower() or "bad" in token_mint_address.lower():
            score -= 0.2
        # Ajout d'un bruit pseudo-aléatoire
        score += (random.random() - 0.5) * 0.1
        score = max(0.0, min(1.0, score))
        elapsed = (time.time() - start) * 1000
        logger.info(f"Prédiction x2 en 10min pour {token_mint_address}: score={score:.2f} (calculé en {elapsed:.1f}ms)")
        if elapsed > 800:
            logger.warning(f"Prédiction trop lente: {elapsed:.1f}ms")
        return score > 0.5
    async def _detect_creator_wallets(self, token_mint_address: str):
        """Détecte tous les comptes liés au créateur du token (via graphe, signatures, transferts, pools)."""
        # À remplacer par une vraie détection blockchain
        # Ici, on simule avec une liste factice
        return [f"wallet_{token_mint_address}_1", f"wallet_{token_mint_address}_2"]

    async def evaluate_held_tokens_for_sale(self, token_mint_address: str, current_price: float, whale_selling: bool = False) -> None:
        """
        Évalue si un token détenu doit être vendu (take profit, stop loss, trailing, signaux dump).
        """
        try:
            if self.simulation_mode:
                result = {
                    "token": token_mint_address,
                    "price": current_price,
                    "action": "sell",
                    "whale_selling": whale_selling,
                    "timestamp": asyncio.get_event_loop().time()
                }
                self.simulation_results.append(result)
                self.log_trade(result, simulation=True)
                logger.info(f"Simulation mode: sell logged for {token_mint_address}")
                return
            if token_mint_address in self.held_tokens:
            buy_price = self.held_tokens[token_mint_address]["buy_price"]
            profit_multiplier = current_price / buy_price
            creator_wallets = self.held_tokens[token_mint_address].get("creator_wallets", [])
            logger.info(f"Evaluating {token_mint_address}: Buy Price={buy_price}, Current Price={current_price}, Multiplier={profit_multiplier:.2f}")
            # Trailing stop : stop loss dynamique après achat
            trailing_stop_percent = getattr(self, 'trailing_stop_percent', 0.15) # 15% par défaut
            if 'max_price' not in self.held_tokens[token_mint_address]:
                self.held_tokens[token_mint_address]['max_price'] = buy_price
            # Met à jour le plus haut atteint
            if current_price > self.held_tokens[token_mint_address]['max_price']:
                self.held_tokens[token_mint_address]['max_price'] = current_price
            # Si le prix redescend de plus de trailing_stop_percent depuis le plus haut, vente
            max_price = self.held_tokens[token_mint_address]['max_price']
            if current_price < max_price * (1 - trailing_stop_percent):
                logger.warning(f"[TRAILING STOP] Selling {token_mint_address}: Price dropped >{int(trailing_stop_percent*100)}% from max ({current_price:.4f} < {max_price:.4f}). Vente automatique.")
                await self._execute_sale(token_mint_address)
                # Hook IA/logs après vente réelle
                self.record_real_trade({
                    "token": token_mint_address,
                    "price": current_price,
                    "action": "sell",
                    "timestamp": asyncio.get_event_loop().time()
                })
                for hook in self.ia_hooks:
                    try:
                        hook.on_trade("sell", token_mint_address, current_price)
                    except Exception as e:
                        logger.warning(f"Erreur hook IA après vente : {e}")
                return
            # PRIORITÉ : Take profit automatique à x2
            if profit_multiplier >= self.sell_multiplier:
                logger.info(f"[TAKE PROFIT] Selling {token_mint_address}: Price reached x{self.sell_multiplier} (x{profit_multiplier:.2f}). Vente immédiate.")
                await self._execute_sale(token_mint_address)
                return
            # STOP LOSS : vente immédiate si le prix passe sous le prix d'achat
            if profit_multiplier < 1.0:
                logger.warning(f"[STOP LOSS] Selling {token_mint_address}: Price dropped below buy price (x{profit_multiplier:.2f} < x1.0). Vente automatique pour éviter toute perte.")
                await self._execute_sale(token_mint_address)
                return
            # Détection avancée des signaux de dump (volume, créateur, liquidité)
            if whale_selling or await self._creator_wallet_selling(token_mint_address, creator_wallets):
                logger.warning(f"[DUMP SIGNAL] Selling {token_mint_address}: Dump ou activité suspecte détectée.")
                await self._execute_sale(token_mint_address)
                return
            logger.info(f"No sale conditions met for {token_mint_address}.")
            else:
                logger.debug(f"Not holding {token_mint_address}, skipping sale evaluation.")
        except Exception as e:
            logger.error(f"Erreur evaluate_held_tokens_for_sale : {e}")
    async def _creator_wallet_selling(self, token_mint_address: str, creator_wallets: list) -> bool:
        """Détecte si un wallet du créateur est en train de vendre ou retirer de la liquidité."""
        # À remplacer par une vraie détection blockchain
        # Ici, on simule avec une probabilité
        import random
        return random.random() > 0.7
    def export_simulation_report(self, filename: str = "simulation_report.csv") -> None:
        """Exporte le rapport de simulation au format CSV."""
        import csv
        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["token", "price", "action", "whale_selling", "timestamp"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.simulation_results:
                    writer.writerow(row)
            logger.info(f"Rapport simulation exporté : {filename}")
        except Exception as e:
            logger.error(f"Erreur export rapport simulation : {e}")

    async def _execute_sale(self, token_mint_address: str) -> None:
        """Exécute la vente d'un token détenu (tout le montant)."""
        try:
            logger.info(f"Attempting to sell all of {token_mint_address}")
            amount = self.held_tokens[token_mint_address]["buy_amount"]
            success = await self.order_executor.execute_sell(token_mint_address, amount)
            if success:
                logger.success(f"Successfully sold {token_mint_address}.")
                del self.held_tokens[token_mint_address]
            else:
                logger.error(f"Failed to sell {token_mint_address}.")
        except Exception as e:
            logger.error(f"Erreur _execute_sale : {e}")