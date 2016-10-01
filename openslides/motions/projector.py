from ..core.exceptions import ProjectorException
from ..utils.collection import CollectionElement
from ..utils.projector import ProjectorElement
from .models import Motion, MotionBlock


class MotionSlide(ProjectorElement):
    """
    Slide definitions for Motion model.
    """
    name = 'motions/motion'

    def check_data(self):
        if not Motion.objects.filter(pk=self.config_entry.get('id')).exists():
            raise ProjectorException('Motion does not exist.')

    def get_requirements(self, config_entry):
        try:
            motion = Motion.objects.get(pk=config_entry.get('id'))
        except Motion.DoesNotExist:
            # Motion does not exist. Just do nothing.
            pass
        else:
            yield motion
            yield motion.agenda_item
            yield motion.state.workflow
            yield from motion.submitters.all()
            yield from motion.supporters.all()

    def get_collection_elements_required_for_this(self, collection_element, config_entry):
        output = super().get_collection_elements_required_for_this(collection_element, config_entry)
        # Full update if motion changes because then we may have new
        # submitters or supporters and therefor need new users.
        #
        # Add some logic here if we support live changing of workflows later.
        #
        if collection_element == CollectionElement.from_values(Motion.get_collection_string(), config_entry.get('id')):
            output.extend(self.get_requirements_as_collection_elements(config_entry))
        return output

    def update_data(self):
        data = None
        try:
            motion = Motion.objects.get(pk=self.config_entry.get('id'))
        except Motion.DoesNotExist:
            # Motion does not exist, so just do nothing.
            pass
        else:
            data = {'agenda_item_id': motion.agenda_item_id}
        return data


class MotionBlockSlide(ProjectorElement):
    """
    Slide definitions for a block of motions (MotionBlock model).
    """
    name = 'motions/motion-block'

    def check_data(self):
        if not MotionBlock.objects.filter(pk=self.config_entry.get('id')).exists():
            raise ProjectorException('MotionBlock does not exist.')

    def get_requirements(self, config_entry):
        try:
            motion_block = MotionBlock.objects.get(pk=config_entry.get('id'))
        except MotionBlock.DoesNotExist:
            # MotionBlock does not exist. Just do nothing.
            pass
        else:
            yield motion_block
            yield motion_block.agenda_item
            yield from motion_block.motion_set.all()

    def get_collection_elements_required_for_this(self, collection_element, config_entry):
        output = super().get_collection_elements_required_for_this(collection_element, config_entry)
        # Full update if a motion changes because then it may be appended to
        # or removed from the block.
        if collection_element.collection_string == Motion.get_collection_string():
            output.extend(self.get_requirements_as_collection_elements(config_entry))
        return output

    def update_data(self):
        data = None
        try:
            motion_block = MotionBlock.objects.get(pk=self.config_entry.get('id'))
        except MotionBlock.DoesNotExist:
            # MotionBlock does not exist, so just do nothing.
            pass
        else:
            data = {'agenda_item_id': motion_block.agenda_item_id}
        return data
