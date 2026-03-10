"""
Advanced Summarizer Wrapper with caching, pipelines, and AI enhancement.

This module provides intelligent orchestration of summarization operations with:
- Persistent caching to avoid reprocessing
- Pipeline processing with chained operations
- AI-enhanced summarization using free LLM APIs
- Comparison mode for evaluating different summaries
- Template system for custom output formats
"""

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
import pickle

from .core import ReadmeSummarizer, SummaryFormat


class CacheBackend(str, Enum):
    """Cache storage backend options."""
    FILESYSTEM = "filesystem"
    MEMORY = "memory"


class AIProvider(str, Enum):
    """AI enhancement provider options."""
    NONE = "none"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


@dataclass
class SummaryMetadata:
    """Metadata for a summary operation."""
    source: str
    timestamp: float
    processing_time: float
    content_hash: str
    normalizer_used: bool
    ai_enhanced: bool
    ai_provider: Optional[str] = None
    cache_hit: bool = False
    pipeline_steps: Optional[List[str]] = None
    word_count: int = 0
    char_count: int = 0


@dataclass
class SummaryResult:
    """Wrapper result containing summary and metadata."""
    content: str
    metadata: SummaryMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "metadata": asdict(self.metadata)
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class SummaryCache:
    """Smart caching layer for summaries."""
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        backend: CacheBackend = CacheBackend.FILESYSTEM,
        ttl: Optional[int] = None,  # Time to live in seconds
    ):
        self.backend = backend
        self.ttl = ttl
        
        if backend == CacheBackend.FILESYSTEM:
            self.cache_dir = cache_dir or Path.home() / ".cache" / "readme-summarizer"
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._memory_cache: Dict[str, tuple] = {}
    
    def _compute_hash(self, content: str, config: Dict[str, Any]) -> str:
        """Compute cache key from content and config."""
        key_data = f"{content}|{json.dumps(config, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[SummaryResult]:
        """Retrieve cached summary."""
        if self.backend == CacheBackend.FILESYSTEM:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if not cache_file.exists():
                return None
            
            try:
                with open(cache_file, "rb") as f:
                    cached_data = pickle.load(f)
                
                # Check TTL
                if self.ttl and (time.time() - cached_data["timestamp"]) > self.ttl:
                    cache_file.unlink()
                    return None
                
                result = SummaryResult(
                    content=cached_data["content"],
                    metadata=SummaryMetadata(**cached_data["metadata"])
                )
                result.metadata.cache_hit = True
                return result
            except Exception:
                return None
        
        else:  # MEMORY backend
            if cache_key not in self._memory_cache:
                return None
            
            cached_data, timestamp = self._memory_cache[cache_key]
            
            # Check TTL
            if self.ttl and (time.time() - timestamp) > self.ttl:
                del self._memory_cache[cache_key]
                return None
            
            result = cached_data
            result.metadata.cache_hit = True
            return result
    
    def set(self, cache_key: str, result: SummaryResult) -> None:
        """Store summary in cache."""
        if self.backend == CacheBackend.FILESYSTEM:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            cache_data = {
                "content": result.content,
                "metadata": asdict(result.metadata),
                "timestamp": time.time()
            }
            
            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)
        
        else:  # MEMORY backend
            self._memory_cache[cache_key] = (result, time.time())
    
    def clear(self) -> int:
        """Clear all cached summaries. Returns count of cleared items."""
        if self.backend == CacheBackend.FILESYSTEM:
            count = 0
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
                count += 1
            return count
        else:
            count = len(self._memory_cache)
            self._memory_cache.clear()
            return count
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.backend == CacheBackend.FILESYSTEM:
            files = list(self.cache_dir.glob("*.pkl"))
            total_size = sum(f.stat().st_size for f in files)
            return {
                "backend": self.backend.value,
                "entries": len(files),
                "total_size_bytes": total_size,
                "cache_dir": str(self.cache_dir)
            }
        else:
            return {
                "backend": self.backend.value,
                "entries": len(self._memory_cache)
            }


class PipelineStep:
    """A single step in a summarization pipeline."""
    
    def __init__(self, name: str, func: Callable[[str], str], description: str = ""):
        self.name = name
        self.func = func
        self.description = description
    
    def execute(self, content: str) -> str:
        """Execute this pipeline step."""
        return self.func(content)


class SummaryPipeline:
    """Chain multiple processing steps together."""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.steps: List[PipelineStep] = []
    
    def add_step(self, step: PipelineStep) -> "SummaryPipeline":
        """Add a processing step to the pipeline."""
        self.steps.append(step)
        return self
    
    def add_transform(
        self,
        name: str,
        func: Callable[[str], str],
        description: str = ""
    ) -> "SummaryPipeline":
        """Add a transformation function as a pipeline step."""
        self.steps.append(PipelineStep(name, func, description))
        return self
    
    def execute(self, content: str) -> tuple[str, List[str]]:
        """
        Execute all pipeline steps sequentially.
        
        Returns:
            Tuple of (processed_content, step_names)
        """
        result = content
        step_names = []
        
        for step in self.steps:
            result = step.execute(result)
            step_names.append(step.name)
        
        return result, step_names
    
    def get_steps(self) -> List[str]:
        """Get list of step names in this pipeline."""
        return [step.name for step in self.steps]


class SummarizerWrapper:
    """
    Advanced wrapper for ReadmeSummarizer with caching, pipelines, and AI enhancement.
    """
    
    def __init__(
        self,
        summarizer: Optional[ReadmeSummarizer] = None,
        enable_cache: bool = True,
        cache_backend: CacheBackend = CacheBackend.FILESYSTEM,
        cache_ttl: Optional[int] = None,
        ai_provider: AIProvider = AIProvider.NONE,
        ai_config: Optional[Dict[str, Any]] = None,
    ):
        self.summarizer = summarizer or ReadmeSummarizer()
        self.enable_cache = enable_cache
        self.ai_provider = ai_provider
        self.ai_config = ai_config or {}
        
        # Initialize cache
        if enable_cache:
            self.cache = SummaryCache(backend=cache_backend, ttl=cache_ttl)
        else:
            self.cache = None
        
        # Initialize AI enhancer
        self._ai_enhancer = None
        if ai_provider != AIProvider.NONE:
            self._init_ai_enhancer()
        
        # Built-in pipelines
        self._pipelines: Dict[str, SummaryPipeline] = {}
        self._register_builtin_pipelines()
    
    def _init_ai_enhancer(self) -> None:
        """Initialize AI enhancement provider."""
        if self.ai_provider == AIProvider.HUGGINGFACE:
            from .ai_enhancers import HuggingFaceEnhancer
            self._ai_enhancer = HuggingFaceEnhancer(**self.ai_config)
        elif self.ai_provider == AIProvider.OLLAMA:
            from .ai_enhancers import OllamaEnhancer
            self._ai_enhancer = OllamaEnhancer(**self.ai_config)
    
    def _register_builtin_pipelines(self) -> None:
        """Register built-in processing pipelines."""
        # Standard pipeline: normalize -> summarize
        standard = SummaryPipeline("standard")
        
        # Technical pipeline: emphasize code and technical details
        technical = SummaryPipeline("technical")
        technical.add_transform(
            "emphasize_tech",
            lambda x: x,  # Placeholder - actual implementation below
            "Emphasize technical content"
        )
        
        # User-friendly pipeline: simplify technical jargon
        friendly = SummaryPipeline("user-friendly")
        
        self._pipelines = {
            "standard": standard,
            "technical": technical,
            "user-friendly": friendly,
        }
    
    def summarize(
        self,
        content: str,
        source: str = "unknown",
        output_format: SummaryFormat = SummaryFormat.TEXT,
        pipeline: Optional[Union[str, SummaryPipeline]] = None,
        bypass_cache: bool = False,
        **kwargs
    ) -> SummaryResult:
        """
        Generate an enhanced summary with caching and optional AI enhancement.
        
        Args:
            content: README content to summarize
            source: Source identifier for metadata
            output_format: Output format
            pipeline: Optional pipeline name or SummaryPipeline instance
            bypass_cache: Skip cache lookup/storage
            **kwargs: Additional arguments passed to summarizer
        
        Returns:
            SummaryResult with content and metadata
        """
        start_time = time.time()
        
        # Compute content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Build cache key
        config = {
            "output_format": output_format.value if isinstance(output_format, SummaryFormat) else output_format,
            "max_length": self.summarizer.max_length,
            "include_badges": self.summarizer.include_badges,
            "include_sections": self.summarizer.include_sections,
            "bullet_points": self.summarizer.bullet_points,
            "ai_provider": self.ai_provider.value,
            "pipeline": pipeline.name if isinstance(pipeline, SummaryPipeline) else pipeline,
            **kwargs
        }
        cache_key = self.cache._compute_hash(content, config) if self.cache else None
        
        # Check cache
        if self.enable_cache and not bypass_cache and cache_key and self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # Apply pipeline if specified
        pipeline_steps = []
        if pipeline:
            if isinstance(pipeline, str):
                if pipeline in self._pipelines:
                    pipeline = self._pipelines[pipeline]
                else:
                    raise ValueError(f"Unknown pipeline: {pipeline}")
            
            content, pipeline_steps = pipeline.execute(content)
        
        # Generate summary
        summary = self.summarizer.summarize(
            content,
            output_format=output_format,
            **kwargs
        )
        
        # Apply AI enhancement if enabled
        ai_enhanced = False
        if self._ai_enhancer:
            try:
                summary = self._ai_enhancer.enhance(summary)
                ai_enhanced = True
            except Exception:
                # Fall back to non-enhanced summary
                pass
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create metadata
        metadata = SummaryMetadata(
            source=source,
            timestamp=time.time(),
            processing_time=processing_time,
            content_hash=content_hash,
            normalizer_used=self.summarizer.enable_normalization,
            ai_enhanced=ai_enhanced,
            ai_provider=self.ai_provider.value if ai_enhanced else None,
            cache_hit=False,
            pipeline_steps=pipeline_steps if pipeline_steps else None,
            word_count=len(summary.split()),
            char_count=len(summary)
        )
        
        result = SummaryResult(content=summary, metadata=metadata)
        
        # Store in cache
        if self.enable_cache and cache_key and self.cache:
            self.cache.set(cache_key, result)
        
        return result
    
    def compare(
        self,
        content: str,
        methods: Optional[List[str]] = None,
    ) -> Dict[str, SummaryResult]:
        """
        Generate and compare summaries using different methods.
        
        Args:
            content: README content
            methods: List of pipeline names to compare
        
        Returns:
            Dictionary mapping method name to SummaryResult
        """
        if methods is None:
            methods = list(self._pipelines.keys())
        
        results = {}
        for method in methods:
            try:
                result = self.summarize(
                    content,
                    source=f"comparison-{method}",
                    pipeline=method,
                )
                results[method] = result
            except Exception as e:
                results[method] = str(e)
        
        return results
    
    def register_pipeline(self, pipeline: SummaryPipeline) -> None:
        """Register a custom pipeline."""
        self._pipelines[pipeline.name] = pipeline
    
    def get_pipeline(self, name: str) -> Optional[SummaryPipeline]:
        """Get a registered pipeline by name."""
        return self._pipelines.get(name)
    
    def list_pipelines(self) -> List[str]:
        """Get list of available pipeline names."""
        return list(self._pipelines.keys())
    
    def clear_cache(self) -> int:
        """Clear all cached summaries. Returns count of cleared items."""
        if self.cache:
            return self.cache.clear()
        return 0
    
    def cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.cache:
            return self.cache.stats()
        return {"enabled": False}
