from distribution_manager import DistributionManager
from frontend_manager import FrontendManager

def main():
    distribution_manager = DistributionManager()
    frontend_manager = FrontendManager(distribution_manager)

    # Start the frontend server
    frontend_manager.run()

if __name__ == '__main__':
    main()
