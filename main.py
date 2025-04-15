"""
Main entry point for BigBrain backend.

This module initializes all components and starts the bridge handler
to listen for commands over stdin/stdout.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

from core.parser import CodeParser
from core.graph_builder import GraphBuilder
from core.graph_store import GraphStore
from bridge.handler import BridgeHandler
import config

# Configure logging
logger = logging.getLogger("bigbrain")


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose (bool): Whether to use verbose (DEBUG) logging.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="BigBrain code knowledge graph backend")
    
    parser.add_argument(
        "--graph-file", 
        type=str,
        help=f"Path to the graph file (default: {config.GRAPH_FILE})"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--mode",
        choices=["bridge", "cli"],
        default="bridge",
        help="Operation mode (bridge: listen for stdin/stdout commands, cli: use command line interface)"
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the application.
    """
    args = parse_args()
    setup_logging(args.verbose)
    
    # Determine graph file path
    graph_file_path = Path(args.graph_file) if args.graph_file else config.GRAPH_FILE
    
    try:
        logger.info(f"BigBrain backend starting in {args.mode} mode")
        logger.info(f"Using graph file: {graph_file_path}")
        
        # Initialize components
        graph_store = GraphStore(graph_file_path)
        parser = CodeParser()
        graph_builder = GraphBuilder(graph_store)
        
        # Initialize bridge handler
        bridge_handler = BridgeHandler(graph_builder, parser, graph_store)
        
        if args.mode == "bridge":
            # Start the bridge handler to listen for stdin/stdout commands
            logger.info("Starting bridge handler")
            bridge_handler.listen()
        else:
            # CLI mode is not implemented yet in this file
            # It will be in the cli.py module
            logger.info("CLI mode not available in main.py, use cli.py instead")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Interrupted, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Save the graph before exiting
        try:
            if 'graph_store' in locals():
                logger.info("Saving graph before exit")
                graph_store.save_graph()
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
    
    logger.info("BigBrain backend shutting down")


if __name__ == "__main__":
    main()
