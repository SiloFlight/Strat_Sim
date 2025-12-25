# Project Goal

Build an extensible, event-driven backtesting framework to model algorithmic trading strategy performance. This framework models a market as a system of distinct participants interacting in discrete events. The OOP approach to the simulation should lend to easy extension in the future.

# Implementation Details

This simulator is built around simulating market behavior through discrete events between different components. The simulation represents Trading Strategies, Financial Brokers, Market Exchanges as individual objects that interact under the coordination of the simulation engine.
- Strategy : The strategy component creates intent based on its available information.
- Broker : Communicates intent to exchange and manages portfolio state.
- Market : Controls execution semantics and fill generation.

# Version Log

## V1 Features
- Queue based event simulation
- Single Symbol Simulation
- Broker and Market Component Latency
- Fail-Fast behavior on invalid simulation states.

## V1 Assumptions
- Only Market Order Support
- Fills occur exclusively at bar open
- Orders fulfilled based on order of arrival
- Simulation terminates immediately upon entering invalid state (negative cash balance, short positions)

# Roadmap

## V2
- Multiple Symbol Support
- Limit Orders
- Automatic Simulation Event Creation
- Timestamp-aware fill logic

## Future
- Stochastic Market Data Generation
- Stop + Stop Limit Orders
- Automated Market Data acquisition
- More Realistic execution models



