# v0.4.0 (2024-10-08)

## 💫 New features

- hierachical, multi-source settings manager [[a30ea9f3]](https://github.com/datalad/datasalad/commit/a30ea9f3)
- declare library type-annotated [[a7f1f0f4]](https://github.com/datalad/datasalad/commit/a7f1f0f4)

## 📝 Documentation

- README:
  - use absolute URL to make link work on PyPi too [[47b38029]](https://github.com/datalad/datasalad/commit/47b38029)

# v0.3.0 (2024-09-21)

## Documentation

- fix typos [[fd70937b]](https://github.com/datalad/datasalad/commit/fd70937b)
- update project classifiers [[2c983daa]](https://github.com/datalad/datasalad/commit/2c983daa)
- Contributing guide:
  - describe new developer conveniences [[0a45fd46]](https://github.com/datalad/datasalad/commit/0a45fd46)
  - snipped on releasing a new version [[b82c58c3]](https://github.com/datalad/datasalad/commit/b82c58c3)

## New features

- provide package version at standard location [[a17eb7c0]](https://github.com/datalad/datasalad/commit/a17eb7c0)

# v0.2.1 (2024-07-14)

## Bug Fixes

- `decode_bytes`:
  - error handling led to data loss in subsequent chunks [[722d0305]](https://github.com/datalad/datasalad/commit/722d0305)

# v0.2.0 (2024-07-11)

## New features

- `itertools` collection of iterators that are focused on processing (byte) streams of information collected from subprocesses. This includes basic support for simple pipe-like processing stream, including splitting off, and rejoining certain items in such a stream. These tools extend and interoperate with standard Python utilities for iterables, such as the built-in `itertools`, and the `more_itertools` package. [[3175cafe]](https://github.com/datalad/datasalad/commit/3175cafe)

## Documentation

- show off new features on the frontpage [[751e5bf9]](https://github.com/datalad/datasalad/commit/751e5bf9)
- update project metadata [[72ecde84]](https://github.com/datalad/datasalad/commit/72ecde84)


# v0.1.0 (2024-06-14)

## New features

- `iter_subproc()` utility
- `iterable_subprocess()` utility
- `CommandError` exception

# v0.0.1rc2 (2024-05-14)

- Non-functional test release

# v0.0.1rc1 (2024-05-13)

- Non-functional test release
