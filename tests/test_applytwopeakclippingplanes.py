import numpy
import numpy.random
import numpy.testing
import pytest

import applytwopeakclippingplanes


instance = applytwopeakclippingplanes.ApplyTwoPeakClippingPlanes


@pytest.fixture(scope="function")
def volume_labels():
    labels = numpy.zeros((10, 20, 20), dtype=numpy.uint16)

    # Make some objects that span the whole array
    labels[:, 1:3, 1:3] = 1
    labels[:, 4:6, 4:6] = 2
    labels[:, 8:12, 8:12] = 3

    return labels


@pytest.fixture(scope="function")
def two_peak_reference():
    # Note: this is out of order for easier broadcasting later
    reference = numpy.ones((20, 20, 10), dtype=numpy.uint16)

    # Create some "peaks"
    reference *= numpy.asarray([1, 3, 5, 9, 7, 6, 4, 7, 4, 2], dtype=numpy.uint16)
    reference *= 1000

    # Make the reference noisy
    reference = reference.T
    reference = numpy.random.normal(reference, 100)

    return reference.astype(numpy.uint16)


@pytest.fixture(scope="function")
def single_peak_reference():
    # Note: this is out of order for easier broadcasting later
    reference = numpy.ones((20, 20, 10), dtype=numpy.uint16)

    # Create one "peaks"
    reference *= numpy.asarray([1, 3, 5, 9, 7, 6, 5, 4, 3, 2], dtype=numpy.uint16)
    reference *= 1000

    # Make the reference noisy
    reference = reference.T
    reference = numpy.random.normal(reference, 100)

    return reference.astype(numpy.uint16)


def test_median_two_peak(volume_labels, two_peak_reference, module, object_set_empty, objects_empty,
                         image_set_empty, image_empty, workspace_empty):
    labels = volume_labels.copy()
    reference = two_peak_reference.copy()

    objects_empty.segmented = labels
    image_empty.pixel_data = reference

    module.x_name.value = "InputObjects"
    module.y_name.value = "OutputObjects"
    module.reference_name.value = "example"

    module.aggregation_method.value = applytwopeakclippingplanes.METHOD_MEDIAN

    module.run(workspace_empty)

    actual = object_set_empty.get_objects("OutputObjects").segmented

    expected = labels.copy()
    # Everything outside of the peaks should be trimmed
    expected[:3] = 0
    expected[-2:] = 0

    numpy.testing.assert_array_equal(actual, expected)


def test_sum_two_peak(volume_labels, two_peak_reference, module, object_set_empty, objects_empty,
                      image_set_empty, image_empty, workspace_empty):
    labels = volume_labels.copy()
    reference = two_peak_reference.copy()

    objects_empty.segmented = labels
    image_empty.pixel_data = reference

    module.x_name.value = "InputObjects"
    module.y_name.value = "OutputObjects"
    module.reference_name.value = "example"

    module.aggregation_method.value = applytwopeakclippingplanes.METHOD_SUM

    module.run(workspace_empty)

    actual = object_set_empty.get_objects("OutputObjects").segmented

    expected = labels.copy()
    # Everything outside of the peaks should be trimmed
    expected[:3] = 0
    expected[-2:] = 0

    numpy.testing.assert_array_equal(actual, expected)


def test_padding_out(volume_labels, two_peak_reference, module, object_set_empty, objects_empty,
                     image_set_empty, image_empty, workspace_empty):
    labels = volume_labels.copy()
    reference = two_peak_reference.copy()

    objects_empty.segmented = labels
    image_empty.pixel_data = reference

    module.x_name.value = "InputObjects"
    module.y_name.value = "OutputObjects"
    module.reference_name.value = "example"

    module.aggregation_method.value = applytwopeakclippingplanes.METHOD_MEDIAN
    module.top_padding.value = -1
    module.bottom_padding.value = 2

    module.run(workspace_empty)

    actual = object_set_empty.get_objects("OutputObjects").segmented

    expected = labels.copy()
    # Everything outside of the peaks should be trimmed
    # But since we've added padding it should go further than normal
    expected[:1] = 0
    expected[-1:] = 0

    numpy.testing.assert_array_equal(actual, expected)


def test_padding_in(volume_labels, two_peak_reference, module, object_set_empty, objects_empty,
                    image_set_empty, image_empty, workspace_empty):
    labels = volume_labels.copy()
    reference = two_peak_reference.copy()

    objects_empty.segmented = labels
    image_empty.pixel_data = reference

    module.x_name.value = "InputObjects"
    module.y_name.value = "OutputObjects"
    module.reference_name.value = "example"

    module.aggregation_method.value = applytwopeakclippingplanes.METHOD_MEDIAN
    module.top_padding.value = 1
    module.bottom_padding.value = -2

    module.run(workspace_empty)

    actual = object_set_empty.get_objects("OutputObjects").segmented

    expected = labels.copy()
    # Everything outside of the peaks should be trimmed
    # But since we've added padding it should go further than normal
    expected[:5] = 0
    expected[-3:] = 0

    numpy.testing.assert_array_equal(actual, expected)


def test_median_single_peak(volume_labels, single_peak_reference, module, object_set_empty, objects_empty,
                            image_set_empty, image_empty, workspace_empty):
    labels = volume_labels.copy()
    reference = single_peak_reference.copy()

    objects_empty.segmented = labels
    image_empty.pixel_data = reference

    module.x_name.value = "InputObjects"
    module.y_name.value = "OutputObjects"
    module.reference_name.value = "example"

    module.aggregation_method.value = applytwopeakclippingplanes.METHOD_MEDIAN
    module.accept_single.value = True

    module.run(workspace_empty)

    actual = object_set_empty.get_objects("OutputObjects").segmented

    expected = labels.copy()
    # Everything before the bottom
    expected[:3] = 0

    numpy.testing.assert_array_equal(actual, expected)