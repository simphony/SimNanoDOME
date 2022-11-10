"""Integration test examples."""

import unittest

from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto

from .common import generate_cuds, get_key_simulation_cuds
from osp.wrappers.simcoupledreactor.coupledreactorsession import \
    CoupledReactorSession
from osp.wrappers.simcoupledreactor.simple_reactor_engine import \
    simple_reactor_engine


class TestIntegration(unittest.TestCase):
    """Integration test examples."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.template_wrapper = generate_cuds()

    def test_reactor_engine_with_reactor_session(self):
        """Tests the interaction between the session and the engine.

        Tests the interaction between `CoupledReactorSession` and
        `simple_reactor_engine`.
        """
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']
        accuracy_level = key_cuds['accuracy_level']

        with CoupledReactorSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            wrapper.add(source, accuracy_level)

            self.assertRaises(
                AttributeError,
                lambda: getattr(session, 'eng')
            )
            self.assertFalse(session._initialized)

            session.run()

            self.assertTrue(session._initialized)
            self.assertTrue(isinstance(session.eng,
                                       simple_reactor_engine))

            expected_dt = 0.00022782407805060085
            self.assertLessEqual(abs(expected_dt - session.eng.dt()),
                                 1e-3)


if __name__ == '__main__':
    unittest.main()
