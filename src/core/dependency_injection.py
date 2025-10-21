"""
Dependency Injection Container

Provides a simple, type-safe dependency injection system
for better testability and flexibility.
"""
import logging
from typing import TypeVar, Type, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Lifetime(Enum):
    """Service lifetime scope"""
    SINGLETON = "singleton"  # One instance for entire application
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"        # One instance per scope/request


@dataclass
class ServiceDescriptor:
    """Describes how to create a service"""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: Lifetime = Lifetime.SINGLETON


class DIContainer:
    """
    Dependency Injection Container

    Features:
    - Type-safe registration and resolution
    - Multiple lifetime scopes (singleton, transient, scoped)
    - Factory functions
    - Instance registration
    - Automatic dependency resolution
    """

    def __init__(self):
        """Initialize DI container"""
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        logger.info("Dependency injection container initialized")

    def register_singleton(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None,
        instance: Optional[T] = None
    ):
        """
        Register a singleton service (one instance for entire app)

        Args:
            service_type: Interface or abstract class
            implementation: Concrete implementation (optional if using factory/instance)
            factory: Factory function to create instance
            instance: Pre-created instance

        Example:
            container.register_singleton(IAnalyzer, SentimentAnalyzer)
            container.register_singleton(ICache, factory=lambda: RedisCache())
            container.register_singleton(ILogger, instance=my_logger)
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation,
            factory=factory,
            instance=instance,
            lifetime=Lifetime.SINGLETON
        )

        self._services[service_type] = descriptor
        logger.debug(f"Registered singleton: {service_type.__name__}")

    def register_transient(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None
    ):
        """
        Register a transient service (new instance every time)

        Args:
            service_type: Interface or abstract class
            implementation: Concrete implementation
            factory: Factory function

        Example:
            container.register_transient(IRequest, HttpRequest)
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation,
            factory=factory,
            lifetime=Lifetime.TRANSIENT
        )

        self._services[service_type] = descriptor
        logger.debug(f"Registered transient: {service_type.__name__}")

    def register_scoped(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None
    ):
        """
        Register a scoped service (one instance per scope)

        Args:
            service_type: Interface or abstract class
            implementation: Concrete implementation
            factory: Factory function

        Example:
            container.register_scoped(ISession, DatabaseSession)
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation,
            factory=factory,
            lifetime=Lifetime.SCOPED
        )

        self._services[service_type] = descriptor
        logger.debug(f"Registered scoped: {service_type.__name__}")

    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service instance

        Args:
            service_type: Type to resolve

        Returns:
            Instance of the requested type

        Raises:
            KeyError: If service not registered
            RuntimeError: If service cannot be created

        Example:
            analyzer = container.resolve(ISentimentAnalyzer)
        """
        if service_type not in self._services:
            raise KeyError(
                f"Service not registered: {service_type.__name__}. "
                f"Available services: {list(self._services.keys())}"
            )

        descriptor = self._services[service_type]

        # Handle different lifetimes
        if descriptor.lifetime == Lifetime.SINGLETON:
            return self._resolve_singleton(descriptor)
        elif descriptor.lifetime == Lifetime.TRANSIENT:
            return self._create_instance(descriptor)
        elif descriptor.lifetime == Lifetime.SCOPED:
            # For simplicity, scoped acts like singleton in this implementation
            # In a full framework, this would use scope objects
            return self._resolve_singleton(descriptor)
        else:
            raise RuntimeError(f"Unknown lifetime: {descriptor.lifetime}")

    def _resolve_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """Resolve or create singleton instance"""
        service_type = descriptor.service_type

        # Check if already created
        if service_type in self._singletons:
            return self._singletons[service_type]

        # Check if instance provided at registration
        if descriptor.instance is not None:
            self._singletons[service_type] = descriptor.instance
            return descriptor.instance

        # Create new instance
        instance = self._create_instance(descriptor)
        self._singletons[service_type] = instance

        logger.debug(f"Created singleton instance: {service_type.__name__}")
        return instance

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create a new instance of a service"""
        # Use factory if provided
        if descriptor.factory is not None:
            try:
                return descriptor.factory()
            except Exception as e:
                raise RuntimeError(
                    f"Factory failed for {descriptor.service_type.__name__}: {e}"
                )

        # Use implementation type
        if descriptor.implementation_type is not None:
            try:
                # Try to resolve constructor dependencies
                return self._auto_inject(descriptor.implementation_type)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create {descriptor.implementation_type.__name__}: {e}"
                )

        # No way to create instance
        raise RuntimeError(
            f"No factory or implementation for {descriptor.service_type.__name__}"
        )

    def _auto_inject(self, cls: Type[T]) -> T:
        """
        Automatically inject constructor dependencies

        Uses type hints to resolve dependencies

        Args:
            cls: Class to instantiate

        Returns:
            Instance with dependencies injected
        """
        import inspect

        # Get constructor signature
        sig = inspect.signature(cls.__init__)

        # Resolve each parameter
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue

            # Get type hint
            param_type = param.annotation

            if param_type == inspect.Parameter.empty:
                # No type hint, skip
                continue

            # Try to resolve from container
            if param_type in self._services:
                kwargs[param_name] = self.resolve(param_type)

        # Create instance
        return cls(**kwargs)

    def is_registered(self, service_type: Type) -> bool:
        """
        Check if a service is registered

        Args:
            service_type: Type to check

        Returns:
            True if registered
        """
        return service_type in self._services

    def clear(self):
        """Clear all registrations and singletons"""
        self._services.clear()
        self._singletons.clear()
        logger.info("Cleared all service registrations")

    def get_registered_services(self) -> Dict[str, str]:
        """
        Get all registered services

        Returns:
            Dictionary mapping service name -> lifetime
        """
        return {
            service_type.__name__: descriptor.lifetime.value
            for service_type, descriptor in self._services.items()
        }


# Global container instance
_global_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """
    Get or create global DI container

    Returns:
        Global DIContainer instance
    """
    global _global_container

    if _global_container is None:
        _global_container = DIContainer()

    return _global_container


def reset_container():
    """Reset global container (useful for testing)"""
    global _global_container
    if _global_container:
        _global_container.clear()
        _global_container = None


# Convenience decorator for injectable services
def injectable(lifetime: Lifetime = Lifetime.SINGLETON):
    """
    Decorator to mark a class as injectable

    Usage:
        @injectable(Lifetime.SINGLETON)
        class MyService:
            pass

        # Later:
        service = container.resolve(MyService)
    """
    def decorator(cls):
        # Auto-register on import
        container = get_container()
        if lifetime == Lifetime.SINGLETON:
            container.register_singleton(cls, implementation=cls)
        elif lifetime == Lifetime.TRANSIENT:
            container.register_transient(cls, implementation=cls)
        elif lifetime == Lifetime.SCOPED:
            container.register_scoped(cls, implementation=cls)

        return cls

    return decorator


# Example usage and setup
def setup_default_services():
    """
    Setup default service registrations

    Call this at application startup
    """
    container = get_container()

    # Register core services
    try:
        from src.cache.result_cache import get_cache
        from src.utils.performance import get_monitor
        from src.models.ollama_pool import get_pool

        # Register singletons
        container.register_singleton(
            type(get_cache()),
            instance=get_cache()
        )

        container.register_singleton(
            type(get_monitor()),
            instance=get_monitor()
        )

        container.register_singleton(
            type(get_pool()),
            instance=get_pool()
        )

        logger.info("Default services registered")

    except Exception as e:
        logger.warning(f"Failed to register some default services: {e}")
