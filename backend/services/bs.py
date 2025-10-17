"""
Black-Scholes pricing utilities for options
"""

import math

def norm_pdf(x: float) -> float:
 return 1.0 / math.sqrt(2 * math.pi) * math.exp(-0.5 * x * x)

def norm_cdf(x: float) -> float:
 return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def call_price(S, K, T, sigma, r):
 if T <= 0 or sigma <= 0:
 return max(0.0, S - K)
 d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
 d2 = d1 - sigma * math.sqrt(T)
 return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)

def put_price(S, K, T, sigma, r):
 if T <= 0 or sigma <= 0:
 return max(0.0, K - S)
 d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
 d2 = d1 - sigma * math.sqrt(T)
 return K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)

# Greeks (agregabile)

def call_delta(S, K, T, sigma, r):
 if T <= 0 or sigma <= 0:
 return 1.0 if S > K else 0.0
 d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
 return norm_cdf(d1)

def put_delta(S, K, T, sigma, r):
 return call_delta(S, K, T, sigma, r) - 1.0

def d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
 """Calculate d1 parameter for Black-Scholes"""
 if T <= 0 or sigma <= 0:
 return 0.0
 return (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))

def d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
 """Calculate d2 parameter for Black-Scholes"""
 if T <= 0 or sigma <= 0:
 return 0.0
 return d1(S, K, T, r, sigma) - sigma * math.sqrt(T)

def gamma(S: float, K: float, T: float, sigma: float, r: float = 0.045) -> float:
 """Option gamma (same for calls and puts)"""
 if T <= 0 or sigma <= 0:
 return 0.0
 d_1 = d1(S, K, T, r, sigma)
 return math.exp(-0.5 * d_1 * d_1) / (S * sigma * math.sqrt(2 * math.pi * T))

def theta_call(S: float, K: float, T: float, sigma: float, r: float = 0.045) -> float:
 """Call option theta (time decay per day)"""
 if T <= 0:
 return 0.0

 d_1 = d1(S, K, T, r, sigma)
 d_2 = d2(S, K, T, r, sigma)

 theta = -S * math.exp(-0.5 * d_1 * d_1) * sigma / (
 2 * math.sqrt(2 * math.pi * T)
 ) - r * K * math.exp(-r * T) * norm_cdf(d_2)

 return theta / 365.0 # Convert to per-day

def theta_put(S: float, K: float, T: float, sigma: float, r: float = 0.045) -> float:
 """Put option theta (time decay per day)"""
 if T <= 0:
 return 0.0

 d_1 = d1(S, K, T, r, sigma)
 d_2 = d2(S, K, T, r, sigma)

 theta = -S * math.exp(-0.5 * d_1 * d_1) * sigma / (
 2 * math.sqrt(2 * math.pi * T)
 ) + r * K * math.exp(-r * T) * norm_cdf(-d_2)

 return theta / 365.0 # Convert to per-day

def vega(S: float, K: float, T: float, sigma: float, r: float = 0.045) -> float:
 """Option vega (sensitivity to volatility)"""
 if T <= 0:
 return 0.0

 d_1 = d1(S, K, T, r, sigma)
 return (
 S * math.sqrt(T) * math.exp(-0.5 * d_1 * d_1) / math.sqrt(2 * math.pi) / 100.0
 )

# ADD (sub cele existente) - aliases pentru compatibilitate cu builder_engine
def bs_gamma(S, K, T, sigma, r):
 if T <= 0 or sigma <= 0:
 return 0.0
 d1_val = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
 return (1.0 / (S * sigma * math.sqrt(T) * math.sqrt(2 * math.pi))) * math.exp(
 -0.5 * d1_val * d1_val
 )

def bs_vega(S, K, T, sigma, r):
 if T <= 0 or sigma <= 0:
 return 0.0
 d1_val = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
 return (
 S
 * math.sqrt(T)
 * (1.0 / math.sqrt(2 * math.pi))
 * math.exp(-0.5 * d1_val * d1_val)
 ) # per 1.0 (nu %)

def call_theta(S, K, T, sigma, r):
 if T <= 0 or sigma <= 0:
 return 0.0
 d1_val = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
 d2_val = d1_val - sigma * math.sqrt(T)
 term1 = -(
 S * (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * d1_val * d1_val) * sigma
 ) / (2 * math.sqrt(T))
 term2 = -r * K * math.exp(-r * T) * norm_cdf(d2_val)
 return term1 + term2 # per an

def put_theta(S, K, T, sigma, r):
 if T <= 0 or sigma <= 0:
 return 0.0
 d1_val = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
 d2_val = d1_val - sigma * math.sqrt(T)
 term1 = -(
 S * (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * d1_val * d1_val) * sigma
 ) / (2 * math.sqrt(T))
 term2 = +r * K * math.exp(-r * T) * norm_cdf(-d2_val)
 return term1 + term2 # per an
