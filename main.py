from menu import BudgetMenu


def main():
    """Entry point"""
    try:
        menu = BudgetMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
