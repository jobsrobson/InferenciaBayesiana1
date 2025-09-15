"""
Módulo para modelos bayesianos
Autor: Robson Jobs
"""

import numpy as np
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional, List, Tuple
import warnings

# Imports para modelagem bayesiana
try:
    import pymc as pm
    import arviz as az
    from scipy import stats
    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False
    warnings.warn("PyMC não está disponível. Modelos bayesianos não funcionarão.")

class BayesianModels:
    """Classe para implementação de modelos bayesianos"""
    
    def __init__(self):
        self.model = None
        self.trace = None
        self.summary = None
        
    def check_dependencies(self) -> bool:
        """Verifica se as dependências estão disponíveis"""
        return PYMC_AVAILABLE
    
    def linear_regression(self, 
                         X: np.ndarray, 
                         y: np.ndarray,
                         n_samples: int = 2000,
                         n_chains: int = 2,
                         tune: int = 1000) -> Dict[str, Any]:
        """
        Implementa regressão linear bayesiana
        
        Args:
            X: Variáveis independentes
            y: Variável dependente
            n_samples: Número de amostras MCMC
            n_chains: Número de cadeias
            tune: Passos de tuning
            
        Returns:
            Dicionário com resultados do modelo
        """
        if not self.check_dependencies():
            return {'error': 'PyMC não está disponível'}
        
        try:
            with pm.Model() as self.model:
                # Priors
                alpha = pm.Normal('alpha', mu=0, sigma=10)
                beta = pm.Normal('beta', mu=0, sigma=10, shape=X.shape[1])
                sigma = pm.HalfNormal('sigma', sigma=1)
                
                # Likelihood
                mu = alpha + pm.math.dot(X, beta)
                y_obs = pm.Normal('y_obs', mu=mu, sigma=sigma, observed=y)
                
                # Sampling
                self.trace = pm.sample(
                    draws=n_samples,
                    chains=n_chains,
                    tune=tune,
                    return_inferencedata=True,
                    progressbar=False
                )
            
            # Gerar resumo
            self.summary = az.summary(self.trace)
            
            return {
                'status': 'success',
                'model': self.model,
                'trace': self.trace,
                'summary': self.summary,
                'diagnostics': self._run_diagnostics()
            }
            
        except Exception as e:
            return {'error': f'Erro na regressão linear: {str(e)}'}
    
    def logistic_regression(self,
                           X: np.ndarray,
                           y: np.ndarray,
                           n_samples: int = 2000,
                           n_chains: int = 2,
                           tune: int = 1000) -> Dict[str, Any]:
        """
        Implementa regressão logística bayesiana
        
        Args:
            X: Variáveis independentes
            y: Variável dependente (binária)
            n_samples: Número de amostras MCMC
            n_chains: Número de cadeias
            tune: Passos de tuning
            
        Returns:
            Dicionário com resultados do modelo
        """
        if not self.check_dependencies():
            return {'error': 'PyMC não está disponível'}
        
        try:
            with pm.Model() as self.model:
                # Priors
                alpha = pm.Normal('alpha', mu=0, sigma=10)
                beta = pm.Normal('beta', mu=0, sigma=10, shape=X.shape[1])
                
                # Likelihood
                logit_p = alpha + pm.math.dot(X, beta)
                p = pm.Deterministic('p', pm.math.sigmoid(logit_p))
                y_obs = pm.Bernoulli('y_obs', p=p, observed=y)
                
                # Sampling
                self.trace = pm.sample(
                    draws=n_samples,
                    chains=n_chains,
                    tune=tune,
                    return_inferencedata=True,
                    progressbar=False
                )
            
            self.summary = az.summary(self.trace)
            
            return {
                'status': 'success',
                'model': self.model,
                'trace': self.trace,
                'summary': self.summary,
                'diagnostics': self._run_diagnostics()
            }
            
        except Exception as e:
            return {'error': f'Erro na regressão logística: {str(e)}'}
    
    def hierarchical_model(self,
                          data: pd.DataFrame,
                          group_col: str,
                          target_col: str,
                          n_samples: int = 2000) -> Dict[str, Any]:
        """
        Implementa modelo hierárquico bayesiano
        
        Args:
            data: DataFrame com os dados
            group_col: Coluna de agrupamento
            target_col: Coluna alvo
            n_samples: Número de amostras
            
        Returns:
            Dicionário com resultados do modelo
        """
        if not self.check_dependencies():
            return {'error': 'PyMC não está disponível'}
        
        try:
            # Preparar dados
            groups = data[group_col].astype('category').cat.codes.values
            y = data[target_col].values
            n_groups = len(data[group_col].unique())
            
            with pm.Model() as self.model:
                # Hiperpriors
                mu_alpha = pm.Normal('mu_alpha', mu=0, sigma=10)
                sigma_alpha = pm.HalfNormal('sigma_alpha', sigma=1)
                
                # Priors específicos do grupo
                alpha = pm.Normal('alpha', mu=mu_alpha, sigma=sigma_alpha, shape=n_groups)
                sigma = pm.HalfNormal('sigma', sigma=1)
                
                # Likelihood
                y_obs = pm.Normal('y_obs', mu=alpha[groups], sigma=sigma, observed=y)
                
                # Sampling
                self.trace = pm.sample(
                    draws=n_samples,
                    return_inferencedata=True,
                    progressbar=False
                )
            
            self.summary = az.summary(self.trace)
            
            return {
                'status': 'success',
                'model': self.model,
                'trace': self.trace,
                'summary': self.summary,
                'groups': data[group_col].unique().tolist()
            }
            
        except Exception as e:
            return {'error': f'Erro no modelo hierárquico: {str(e)}'}
    
    def _run_diagnostics(self) -> Dict[str, Any]:
        """
        Executa diagnósticos do modelo
        
        Returns:
            Dicionário com métricas diagnósticas
        """
        if self.trace is None:
            return {}
        
        try:
            diagnostics = {}
            
            # R-hat
            rhat = az.rhat(self.trace)
            diagnostics['rhat'] = rhat.to_dict() if hasattr(rhat, 'to_dict') else str(rhat)
            
            # Effective sample size
            ess = az.ess(self.trace)
            diagnostics['ess'] = ess.to_dict() if hasattr(ess, 'to_dict') else str(ess)
            
            # MCSE (Monte Carlo Standard Error)
            mcse = az.mcse(self.trace)
            diagnostics['mcse'] = mcse.to_dict() if hasattr(mcse, 'to_dict') else str(mcse)
            
            return diagnostics
            
        except Exception as e:
            return {'error': f'Erro nos diagnósticos: {str(e)}'}
    
    def model_comparison(self, models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compara múltiplos modelos usando critérios de informação
        
        Args:
            models: Lista de modelos para comparar
            
        Returns:
            Dicionário com resultados da comparação
        """
        if not self.check_dependencies():
            return {'error': 'PyMC não está disponível'}
        
        try:
            model_dict = {}
            for i, model_result in enumerate(models):
                if 'trace' in model_result:
                    model_dict[f'model_{i}'] = model_result['trace']
            
            if len(model_dict) < 2:
                return {'error': 'Necessário pelo menos 2 modelos para comparação'}
            
            comparison = az.compare(model_dict)
            
            return {
                'status': 'success',
                'comparison': comparison,
                'best_model': comparison.index[0]
            }
            
        except Exception as e:
            return {'error': f'Erro na comparação: {str(e)}'}
    
    def predict(self, X_new: np.ndarray, n_samples: int = 1000) -> Dict[str, Any]:
        """
        Faz predições usando o modelo treinado
        
        Args:
            X_new: Novos dados para predição
            n_samples: Número de amostras para predição
            
        Returns:
            Dicionário com predições
        """
        if self.model is None or self.trace is None:
            return {'error': 'Modelo não foi treinado'}
        
        try:
            with self.model:
                pm.set_data({'X': X_new})
                posterior_predictive = pm.sample_posterior_predictive(
                    self.trace, 
                    samples=n_samples,
                    progressbar=False
                )
            
            predictions = posterior_predictive.posterior_predictive
            
            return {
                'status': 'success',
                'predictions': predictions,
                'mean': predictions.mean(),
                'std': predictions.std()
            }
            
        except Exception as e:
            return {'error': f'Erro na predição: {str(e)}'}
    
    def get_model_summary(self) -> str:
        """
        Retorna resumo textual do modelo
        
        Returns:
            String com resumo do modelo
        """
        if self.summary is None:
            return "Nenhum modelo ajustado"
        
        return str(self.summary)