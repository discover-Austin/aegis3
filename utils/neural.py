"""
Pure Python neural network implementation for AEGIS-3.

Provides simple but functional neural networks without external dependencies.
Used for world models, value functions, and learned predictors.
"""

import math
import random
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass, field


def sigmoid(x: float) -> float:
    """Sigmoid activation function."""
    return 1.0 / (1.0 + math.exp(-max(min(x, 500), -500)))  # Clamp to prevent overflow


def tanh(x: float) -> float:
    """Tanh activation function."""
    return math.tanh(x)


def relu(x: float) -> float:
    """ReLU activation function."""
    return max(0.0, x)


def leaky_relu(x: float, alpha: float = 0.01) -> float:
    """Leaky ReLU activation function."""
    return max(alpha * x, x)


def sigmoid_derivative(y: float) -> float:
    """Derivative of sigmoid (given output y)."""
    return y * (1.0 - y)


def tanh_derivative(y: float) -> float:
    """Derivative of tanh (given output y)."""
    return 1.0 - y * y


def relu_derivative(x: float) -> float:
    """Derivative of ReLU."""
    return 1.0 if x > 0 else 0.0


def leaky_relu_derivative(x: float, alpha: float = 0.01) -> float:
    """Derivative of Leaky ReLU."""
    return 1.0 if x > 0 else alpha


class Layer:
    """A fully connected neural network layer."""

    def __init__(
        self,
        input_size: int,
        output_size: int,
        activation: str = 'relu',
        learning_rate: float = 0.01
    ):
        """
        Initialize layer.

        Args:
            input_size: Number of input neurons
            output_size: Number of output neurons
            activation: Activation function ('relu', 'sigmoid', 'tanh', 'leaky_relu')
            learning_rate: Learning rate for weight updates
        """
        self.input_size = input_size
        self.output_size = output_size
        self.learning_rate = learning_rate

        # Xavier/Glorot initialization
        limit = math.sqrt(6.0 / (input_size + output_size))
        self.weights = [
            [random.uniform(-limit, limit) for _ in range(input_size)]
            for _ in range(output_size)
        ]
        self.biases = [random.uniform(-limit, limit) for _ in range(output_size)]

        # Activation function
        self.activation_name = activation
        if activation == 'sigmoid':
            self.activation = sigmoid
            self.activation_derivative = sigmoid_derivative
        elif activation == 'tanh':
            self.activation = tanh
            self.activation_derivative = tanh_derivative
        elif activation == 'relu':
            self.activation = relu
            self.activation_derivative = relu_derivative
        elif activation == 'leaky_relu':
            self.activation = leaky_relu
            self.activation_derivative = leaky_relu_derivative
        else:
            # Linear activation
            self.activation = lambda x: x
            self.activation_derivative = lambda x: 1.0

        # Cache for backpropagation
        self.last_input: Optional[List[float]] = None
        self.last_preactivation: Optional[List[float]] = None
        self.last_output: Optional[List[float]] = None

    def forward(self, inputs: List[float]) -> List[float]:
        """Forward pass through the layer."""
        if len(inputs) != self.input_size:
            raise ValueError(f"Expected {self.input_size} inputs, got {len(inputs)}")

        # Cache input for backprop
        self.last_input = inputs.copy()

        # Compute pre-activation (weighted sum + bias)
        preactivation = []
        for i in range(self.output_size):
            weighted_sum = sum(
                self.weights[i][j] * inputs[j]
                for j in range(self.input_size)
            )
            preactivation.append(weighted_sum + self.biases[i])

        self.last_preactivation = preactivation.copy()

        # Apply activation
        output = [self.activation(z) for z in preactivation]
        self.last_output = output.copy()

        return output

    def backward(self, output_gradient: List[float]) -> List[float]:
        """
        Backward pass (backpropagation).

        Args:
            output_gradient: Gradient of loss w.r.t. layer output

        Returns:
            Gradient of loss w.r.t. layer input
        """
        if self.last_input is None or self.last_output is None:
            raise RuntimeError("Must call forward() before backward()")

        # Compute gradient w.r.t. pre-activation
        if self.activation_name in ('sigmoid', 'tanh'):
            # For sigmoid/tanh, derivative uses output
            activation_gradients = [
                output_gradient[i] * self.activation_derivative(self.last_output[i])
                for i in range(self.output_size)
            ]
        else:
            # For ReLU and others, derivative uses pre-activation
            activation_gradients = [
                output_gradient[i] * self.activation_derivative(self.last_preactivation[i])
                for i in range(self.output_size)
            ]

        # Compute gradient w.r.t. weights and biases
        weight_gradients = [
            [activation_gradients[i] * self.last_input[j]
             for j in range(self.input_size)]
            for i in range(self.output_size)
        ]
        bias_gradients = activation_gradients.copy()

        # Update weights and biases (gradient descent)
        for i in range(self.output_size):
            for j in range(self.input_size):
                self.weights[i][j] -= self.learning_rate * weight_gradients[i][j]
            self.biases[i] -= self.learning_rate * bias_gradients[i]

        # Compute gradient w.r.t. input
        input_gradient = [0.0] * self.input_size
        for j in range(self.input_size):
            input_gradient[j] = sum(
                activation_gradients[i] * self.weights[i][j]
                for i in range(self.output_size)
            )

        return input_gradient


class NeuralNetwork:
    """Multi-layer neural network."""

    def __init__(
        self,
        layer_sizes: List[int],
        activations: Optional[List[str]] = None,
        learning_rate: float = 0.01
    ):
        """
        Initialize neural network.

        Args:
            layer_sizes: Size of each layer (including input and output)
            activations: Activation for each hidden/output layer
            learning_rate: Learning rate for all layers
        """
        self.layer_sizes = layer_sizes
        self.learning_rate = learning_rate

        # Default activations: ReLU for hidden layers, linear for output
        if activations is None:
            activations = ['relu'] * (len(layer_sizes) - 2) + ['linear']

        # Create layers
        self.layers: List[Layer] = []
        for i in range(len(layer_sizes) - 1):
            layer = Layer(
                input_size=layer_sizes[i],
                output_size=layer_sizes[i + 1],
                activation=activations[i],
                learning_rate=learning_rate
            )
            self.layers.append(layer)

    def forward(self, inputs: List[float]) -> List[float]:
        """Forward pass through the network."""
        activations = inputs
        for layer in self.layers:
            activations = layer.forward(activations)
        return activations

    def backward(self, target: List[float], output: List[float]) -> float:
        """
        Backward pass and weight update.

        Args:
            target: Target output
            output: Actual output from forward pass

        Returns:
            Mean squared error loss
        """
        # Compute loss (MSE)
        loss = sum((target[i] - output[i]) ** 2 for i in range(len(target))) / len(target)

        # Compute output gradient (derivative of MSE)
        output_gradient = [
            2.0 * (output[i] - target[i]) / len(target)
            for i in range(len(output))
        ]

        # Backpropagate through layers
        gradient = output_gradient
        for layer in reversed(self.layers):
            gradient = layer.backward(gradient)

        return loss

    def train(
        self,
        inputs: List[float],
        targets: List[float]
    ) -> float:
        """
        Train on a single example.

        Args:
            inputs: Input vector
            targets: Target output vector

        Returns:
            Loss value
        """
        output = self.forward(inputs)
        loss = self.backward(targets, output)
        return loss

    def train_batch(
        self,
        batch: List[Tuple[List[float], List[float]]],
        epochs: int = 1
    ) -> List[float]:
        """
        Train on a batch of examples.

        Args:
            batch: List of (input, target) pairs
            epochs: Number of epochs to train

        Returns:
            List of loss values per epoch
        """
        losses = []
        for epoch in range(epochs):
            epoch_loss = 0.0
            random.shuffle(batch)  # Shuffle for stochastic gradient descent

            for inputs, targets in batch:
                loss = self.train(inputs, targets)
                epoch_loss += loss

            avg_loss = epoch_loss / len(batch)
            losses.append(avg_loss)

        return losses

    def predict(self, inputs: List[float]) -> List[float]:
        """Make a prediction (alias for forward pass)."""
        return self.forward(inputs)

    def get_weights(self) -> List[List[List[List[float]]]]:
        """Get all network weights."""
        return [[layer.weights, layer.biases] for layer in self.layers]

    def set_weights(self, weights: List[List[List[List[float]]]]):
        """Set all network weights."""
        for i, (layer_weights, layer_biases) in enumerate(weights):
            self.layers[i].weights = layer_weights
            self.layers[i].biases = layer_biases


class OnlineNeuralNetwork(NeuralNetwork):
    """
    Neural network optimized for online learning.

    Features:
    - Experience replay buffer
    - Adaptive learning rate
    - Regularization
    """

    def __init__(
        self,
        layer_sizes: List[int],
        activations: Optional[List[str]] = None,
        learning_rate: float = 0.01,
        buffer_size: int = 1000,
        l2_reg: float = 0.0001
    ):
        """
        Initialize online neural network.

        Args:
            layer_sizes: Size of each layer
            activations: Activation functions
            learning_rate: Initial learning rate
            buffer_size: Size of experience replay buffer
            l2_reg: L2 regularization coefficient
        """
        super().__init__(layer_sizes, activations, learning_rate)

        self.buffer_size = buffer_size
        self.l2_reg = l2_reg
        self.experience_buffer: List[Tuple[List[float], List[float]]] = []
        self.training_steps = 0

    def add_experience(self, inputs: List[float], targets: List[float]):
        """Add experience to replay buffer."""
        self.experience_buffer.append((inputs.copy(), targets.copy()))

        # Keep buffer size limited
        if len(self.experience_buffer) > self.buffer_size:
            self.experience_buffer.pop(0)

    def train_with_replay(self, replay_batch_size: int = 32) -> Optional[float]:
        """
        Train on current experience plus replay.

        Args:
            replay_batch_size: Number of replay samples to use

        Returns:
            Average loss
        """
        if not self.experience_buffer:
            return None

        # Sample from replay buffer
        batch_size = min(replay_batch_size, len(self.experience_buffer))
        batch = random.sample(self.experience_buffer, batch_size)

        # Train on batch
        losses = self.train_batch(batch, epochs=1)
        self.training_steps += 1

        # Adaptive learning rate decay
        if self.training_steps % 100 == 0:
            decay_factor = 0.95
            for layer in self.layers:
                layer.learning_rate *= decay_factor

        return losses[0] if losses else None


# Utility functions for creating common architectures

def create_mlp(
    input_size: int,
    output_size: int,
    hidden_sizes: List[int],
    learning_rate: float = 0.01
) -> NeuralNetwork:
    """
    Create a multi-layer perceptron.

    Args:
        input_size: Input dimension
        output_size: Output dimension
        hidden_sizes: Sizes of hidden layers
        learning_rate: Learning rate

    Returns:
        Configured neural network
    """
    layer_sizes = [input_size] + hidden_sizes + [output_size]
    activations = ['relu'] * len(hidden_sizes) + ['linear']
    return NeuralNetwork(layer_sizes, activations, learning_rate)


def create_value_network(state_dim: int, learning_rate: float = 0.01) -> NeuralNetwork:
    """Create a value function network."""
    return create_mlp(state_dim, 1, [64, 32], learning_rate)


def create_policy_network(
    state_dim: int,
    action_dim: int,
    learning_rate: float = 0.01
) -> NeuralNetwork:
    """Create a policy network."""
    layer_sizes = [state_dim, 64, 32, action_dim]
    activations = ['relu', 'relu', 'sigmoid']  # Sigmoid for action probabilities
    return NeuralNetwork(layer_sizes, activations, learning_rate)


def create_world_model_network(
    state_action_dim: int,
    state_dim: int,
    learning_rate: float = 0.01
) -> OnlineNeuralNetwork:
    """
    Create a world model network for state prediction.

    Args:
        state_action_dim: Combined dimension of state and action
        state_dim: State dimension (output)
        learning_rate: Learning rate

    Returns:
        Online neural network for world modeling
    """
    layer_sizes = [state_action_dim, 128, 64, state_dim]
    activations = ['relu', 'relu', 'linear']
    return OnlineNeuralNetwork(layer_sizes, activations, learning_rate)
