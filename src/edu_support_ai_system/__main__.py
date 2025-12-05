"""Entry point for edu_support_ai_system FastAPI application"""

import argparse
import uvicorn

from . import config


def main():
    """Run the FastAPI application"""
    parser = argparse.ArgumentParser(description="Educational Support AI System API")
    parser.add_argument(
        "--host",
        type=str,
        default=config.HOST,
        help=f"Host to bind to (default: {config.HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.PORT,
        help=f"Port to bind to (default: {config.PORT})",
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    print(f"Starting Educational Support AI System API on {args.host}:{args.port}")
    print(f"API Documentation: http://{args.host}:{args.port}/docs")
    print(f"ReDoc Documentation: http://{args.host}:{args.port}/redoc")

    uvicorn.run(
        "edu_support_ai_system.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
