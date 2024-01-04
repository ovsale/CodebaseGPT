import sys

from codebasegpt.app import main


try:
    main()
    pass
except KeyboardInterrupt:
    print("\nApp terminated")
    # sys.exit(0)

print()

