import json
import time
import threading
from loguru import logger

class AIAutoOptimizer:
    """
    Surveille les logs de trades et ajuste automatiquement les paramètres du bot en temps réel.
    """
    def __init__(self, decision_module, simulation_log='simulation_trades.log', real_log='real_trades.log', interval=60):
        self.decision_module = decision_module
        self.simulation_log = simulation_log
        self.real_log = real_log
        self.interval = interval  # en secondes
        self.running = False
        self.last_sim_len = 0
        self.last_real_len = 0

    def analyze_and_adjust(self):
        """
        Analyse les logs et ajuste les paramètres du bot selon les performances.
        """
        # Analyse simulation
        sim_trades = self._read_log(self.simulation_log)
        real_trades = self._read_log(self.real_log)
        sim_profit = self._compute_profit(sim_trades)
        real_profit = self._compute_profit(real_trades)

        # Log pour suivi
        logger.info(f"[AI Optimizer] Profit simulation: {sim_profit:.4f} | Profit réel: {real_profit:.4f}")

        # Ajustement automatique (exemple simple)
        if real_profit < 0:
            # Si pertes réelles, réduire le montant d'achat et augmenter le seuil de vente
            self.decision_module.buy_amount_sol = max(0.01, self.decision_module.buy_amount_sol * 0.9)
            self.decision_module.sell_multiplier = min(2.0, self.decision_module.sell_multiplier + 0.05)
            logger.info(f"[AI Optimizer] Ajustement: buy_amount_sol -> {self.decision_module.buy_amount_sol}, sell_multiplier -> {self.decision_module.sell_multiplier}")
        elif real_profit > 0.1:
            # Si profit, augmenter légèrement le montant d'achat
            self.decision_module.buy_amount_sol = min(1.0, self.decision_module.buy_amount_sol * 1.05)
            logger.info(f"[AI Optimizer] Ajustement: buy_amount_sol -> {self.decision_module.buy_amount_sol}")

    def _read_log(self, log_file):
        trades = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        trades.append(json.loads(line.strip()))
                    except Exception:
                        continue
        except FileNotFoundError:
            pass
        return trades

    def _compute_profit(self, trades):
        profit = 0.0
        buy_prices = {}
        for entry in trades:
            if entry.get('action') == 'buy':
                buy_prices[entry['token']] = entry['price']
            elif entry.get('action') == 'sell' and entry['token'] in buy_prices:
                profit += entry['price'] - buy_prices[entry['token']]
        return profit

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False

    def _run(self):
        logger.info("[AI Optimizer] Démarrage de l'optimisation automatique continue.")
        while self.running:
            self.analyze_and_adjust()
            time.sleep(self.interval)

    def on_new_trade(self, trade_entry, simulation=True):
        """
        À appeler à chaque nouveau trade (vente) pour déclencher l’analyse et l’ajustement immédiat.
        """
        self.log_trade(trade_entry, simulation=simulation)
        self.analyze_and_adjust()

# Exemple d'intégration (à placer dans main.py ou backend)
# from trading.decision_module import DecisionModule
# from ai_analysis.ai_auto_optimizer import AIAutoOptimizer
# decision_module = DecisionModule(...)
# ai_optimizer = AIAutoOptimizer(decision_module)
# ai_optimizer.start()
